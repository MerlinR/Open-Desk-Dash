import importlib
import os
import shutil
import sqlite3
import tarfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Union

import git
import requests
import toml
from flask import Blueprint, Flask
from open_desk_dash.lib.db_control import get_config_db

GIT_RELEASE_PATH = "https://api.github.com/repos/{author}/{repo}/releases/latest"


@dataclass
class Plugin:
    name: str
    title: str
    description: str
    author: str
    github: str
    path: str
    version: str
    repoCommit: str = ""
    tag: str = ""
    tagName: str = ""
    autoUpdate: bool = True
    pages: List[str] = field(default_factory=list)
    configPath: str = None
    setupFn: Callable = None
    id: int = -1
    added: datetime = datetime.now
    updated: datetime = datetime.now

    @classmethod
    def from_dict(cls, dict_v: dict):
        return cls(**dict_v)

    def save_to_db(self, app: Flask):
        try:
            connection = get_config_db()
            cur = connection.cursor()
            sql = f"INSERT INTO plugins (name, path, title, description, author, github, autoUpdate, tag, version, repoCommit, tagName) VALUES (?,?,?,?,?,?,?,?,?,?,?);"
            cur.execute(
                sql,
                (
                    self.name,
                    self.path,
                    self.title,
                    self.description,
                    self.author,
                    self.github,
                    app.config["config"]["autoUpdatePlugins"],
                    self.tag,
                    self.version,
                    self.repoCommit,
                    self.tagName,
                ),
            )
            connection.commit()
        except Exception as e:
            print("Failed to save plugin registry")
            print(e)
            connection.rollback()
        finally:
            connection.close()


class PluginManager:
    def __init__(self, app: Flask, plugins_dir=str):
        self.app = app
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.load_plugins_from_DB()

    def find_local_plugins(self) -> Dict[str, str]:
        plugins = {}
        for direct in os.listdir(self.plugins_dir):
            full_path = os.path.join(self.plugins_dir, direct)
            if os.path.isdir(full_path):
                for file in Path(full_path).rglob("registry.toml"):
                    plugins[direct] = os.path.dirname(file)
        return plugins

    def find_plugin_root_dir(self, name: str) -> str:
        for direct in os.listdir(self.plugins_dir):
            print(direct)
            if direct == name:
                return os.path.join(self.plugins_dir, direct)

    def register_plugins(self):
        for name, path in self.find_local_plugins().items():
            registry = self.get_plugin_registry(name, path)
            if not registry:
                print(f"Unknown {name} Plugin has no registry File. Skipping")
                continue
            elif registry["name"] not in self.plugins.keys():
                self.plugins[registry["name"]] = Plugin.from_dict(registry)
                self.plugins[registry["name"]].save_to_db(self.app)

    def import_plugins(self):
        for name, plugin in self.plugins.items():

            plugin_setup, plugin_blueprint = self.import_plugin_module(
                name, plugin.path
            )

            if not plugin_blueprint:
                print(f"Skipping {name} Due to no blueprint found")
                continue

            self.app.register_blueprint(plugin_blueprint)

            pages = [
                str(p)
                for p in self.app.url_map.iter_rules()
                if plugin.name in str(p)
                and "static" not in str(p)
                and "config" not in str(p)
            ]

            for p in self.app.url_map.iter_rules():
                if plugin.name in str(p) and "config" in str(p):
                    self.plugins[name].config_page = str(p)

            self.plugins[name].pages = pages
            self.plugins[name].setupFn = plugin_setup

    def import_plugin_module(
        self, module_name: str, path: str
    ) -> Union[Callable, Blueprint]:
        path = path.replace("/", ".")
        module_file = path.split(".")[-1]
        try:
            plugin_api = importlib.import_module(f".{module_file}", path).api
            try:
                plugin_setup = importlib.import_module(f".{module_file}", path).setup
            except AttributeError:
                print(f"{module_name} has no setup function")
                plugin_setup = None
            plugin_api.name = module_name
            plugin_api.static_folder = "./src/static"
            plugin_api.template_folder = "./src"
            plugin_api.url_prefix = f"/{module_name}"
        except ModuleNotFoundError as e:
            print(f"Failed to import {module_name}")
            print(e)
            return None

        return plugin_setup, plugin_api

    def get_plugin_registry(self, name: str, path: str) -> dict:
        registry = os.path.join(path, "registry.toml")
        if os.path.exists(registry):
            config = toml.load(registry)
            config["plugin"]["name"] = name
            config["plugin"]["path"] = path
            return config["plugin"]
        return None

    def run_plugins_setup(self):
        for name, plugin in self.plugins.items():
            if plugin.setupFn:
                try:
                    plugin.setupFn(self.app)
                except Exception as e:
                    print(f"[{name}] Failed to run setup due to:")
                    print(e)

    def load_plugins_from_DB(self):
        try:
            connection = get_config_db()
            connection.row_factory = sqlite3.Row
            cur = connection.cursor()

            cur.execute("SELECT * FROM plugins")
            existing = cur.fetchall()

            for plugin in existing:
                self.plugins[plugin["name"]] = Plugin.from_dict(
                    dict(zip(plugin.keys(), plugin))
                )

        except Exception as e:
            print("Failed to load plugin DB")
            print(e)
        finally:
            connection.close()

        self.remove_missing_plugins()

    def remove_missing_plugins(self):
        try:
            connection = get_config_db()
            connection.row_factory = sqlite3.Row
            cur = connection.cursor()
            cur.execute("SELECT * FROM plugins")

            for row in cur.fetchall():
                if not os.path.exists(row["path"]):
                    print(f"Module {row['name']} Missing... Deleting SQL record")
                    sql = f"DELETE FROM plugins WHERE id = {row['id']};"
                    cur.execute(sql)
                    connection.commit()
                    self.plugins.pop(row["name"], None)

        except Exception as e:
            print("Failed to load plugin DB")
            print(e)
        finally:
            connection.close()

    def find_registry(self, repo: str) -> str:
        for file in Path(repo).rglob("registry.toml"):
            return file.as_posix()

    def plugin_install(self, link: str):
        tmp_repo_path = os.path.join(self.plugins_dir, "new_plugin")
        accountName = link.split("/")[-2]
        repoName = link.split("/")[-1]

        release = self.plugin_api_check(accountName, repoName)

        if release:
            self.plugin_install_release(release, tmp_repo_path)
        else:
            self.plugin_install_repo(link, tmp_repo_path)

        registry_path = os.path.dirname(self.find_registry(tmp_repo_path))

        if not registry_path:
            print("Failed to Install, cancelling")
            return

        pluginName = os.path.basename(registry_path)

        new_plugin_path = os.path.join(self.plugins_dir, f"{accountName}_{pluginName}")
        if os.path.exists(new_plugin_path):
            print("Plugin Already exists, skipping")
            shutil.rmtree(tmp_repo_path)
        else:
            os.rename(tmp_repo_path, new_plugin_path)

        registry = self.get_plugin_registry(
            f"{accountName}_{pluginName}",
            os.path.dirname(self.find_registry(new_plugin_path)),
        )
        if release:
            registry["tag"] = release["tag_name"]
            registry["tagName"] = release["name"]
        else:
            repo = git.Repo(new_plugin_path)
            registry["repoCommit"] = repo.head.object.hexsha

        self.plugins[registry["name"]] = Plugin.from_dict(registry)
        self.plugins[registry["name"]].save_to_db(self.app)

    def plugin_install_release(self, release_info: dict, current_path: str):
        print(f"Version {release_info['tag_name']} - {release_info['name']}")
        try:
            response = requests.get(release_info["tarball_url"], stream=True)
            with tarfile.open(fileobj=response.raw, mode=f"r|gz") as tar:
                tar.extractall(path=current_path)
        except Exception as e:
            print("Failed to download release")
            print(e)
            return

    def plugin_install_repo(self, link: dict, current_path: str):
        try:
            git.Repo.clone_from(link, current_path)
        except Exception as e:
            print(e)
            print(f"Failed to clone repo: {link}")
            return

    def plugin_delete(self, name: str):
        path = self.find_plugin_root_dir(name)
        if os.path.exists(path):
            print("Plugin exists, Deleting")
            shutil.rmtree(path)
            self.remove_missing_plugins()

    def plugin_api_check(self, author: str, repo: str):
        print(GIT_RELEASE_PATH)
        git_api_link = GIT_RELEASE_PATH.format(author=author, repo=repo)
        response = requests.get(git_api_link)
        if response.status_code != 200:
            return None
        return response.json()

    def update_plugins(self):
        for name, plugin in self.plugins.items():
            if plugin.repoCommit:
                self.plugin_repo_update(name)
            elif plugin.tag:
                self.plugin_release_update(name)

    def plugin_repo_version(self, name: str):
        plugin = self.plugins[name]
        repo = git.Repo(plugin["path"])

    def plugin_repo_update(self, name: str):
        plugin = self.plugins[name]

        repo = git.Repo(plugin["path"], search_parent_directories=True)
        remote = git.remote.Remote(repo, "origin")
        behind = 0
        newest = remote.fetch()[0].commit.hexsha
        for change in remote.fetch():
            if change.commit.hexsha != plugin["repoCommit"]:
                behind += 1

        print(f"Behind by {behind} - newest {newest}")
        # import pdb

        # pdb.set_trace()
        # repo.remotes.origin.pull()

    def plugin_release_update(self, name: str):
        plugin = self.plugins[name]

    def __delitem__(self, key):
        del self.plugins[key]

    def clear(self):
        return self.plugins.clear()

    def copy(self):
        return self.plugins.copy()

    def has_key(self, k):
        return k in self.plugins

    def update(self, *args, **kwargs):
        return self.plugins.update(*args, **kwargs)

    def keys(self):
        return self.plugins.keys()

    def values(self):
        return self.plugins.values()

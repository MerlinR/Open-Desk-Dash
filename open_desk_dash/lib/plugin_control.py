import importlib
import os
import shutil
import sqlite3
import tarfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Union

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
    tag: str = ""
    tagName: str = ""
    latestTag: str = ""
    latestTagName: str = ""
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
            sql = f"INSERT INTO plugins (name, path, title, description, author, github, tag, version, tagName, updated) VALUES (?,?,?,?,?,?,?,?,?,?);"
            cur.execute(
                sql,
                (
                    self.name,
                    self.path,
                    self.title,
                    self.description,
                    self.author,
                    self.github,
                    self.tag,
                    self.version,
                    self.tagName,
                    datetime.now(),
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

        if not release:
            print(f"No release found in Repo")
            return

        print(f"Version {release['tag_name']} - {release['name']}")
        try:
            response = requests.get(release["tarball_url"], stream=True)
            with tarfile.open(fileobj=response.raw, mode=f"r|gz") as tar:
                tar.extractall(path=tmp_repo_path)
        except Exception as e:
            print("Failed to download release")
            print(e)
            return

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

        registry["tag"] = release["tag_name"]
        registry["tagName"] = release["name"]

        self.plugins[registry["name"]] = Plugin.from_dict(registry)
        self.plugins[registry["name"]].save_to_db(self.app)

    def plugin_delete(self, name: str):
        path = self.find_plugin_root_dir(name)
        if path and os.path.exists(path):
            print("Plugin exists, Deleting")
            shutil.rmtree(path)

    def plugin_api_check(self, author: str, repo: str):
        git_api_link = GIT_RELEASE_PATH.format(author=author, repo=repo)
        response = requests.get(git_api_link)
        if response.status_code != 200:
            return None
        return response.json()

    def update_plugin_check(self):
        for name, plugin in self.plugins.items():
            if name in ["default_dashboard", "default_weather"]:
                continue
            print(f"Checking {name} for updates")
            accountName = plugin.github.split("/")[-2]
            repoName = plugin.github.split("/")[-1]

            release = self.plugin_api_check(accountName, repoName)
            if not release:
                print(f"{name} has no releases")
                continue

            if (
                release["tag_name"] != plugin.tag
                and self.app.config["config"]["autoUpdate"]
            ):
                print("Out of Date, Auto Updating")
                self.update_plugin(plugin.name)
            elif (
                release["tag_name"] != plugin.tag
                and not self.app.config["config"]["autoUpdate"]
            ):
                print("Out of Date, Plugin set to not Auto update")
                plugin.latestTag = release["tag_name"]
                plugin.latestTagName = release["name"]
            else:
                print(f"{name} is up to date")

    def update_plugin(self, plugin_name: str):
        plugin = self.plugins[plugin_name]
        self.plugin_delete(plugin.name)
        self.plugin_install(plugin.github)

    def __delitem__(self, key):
        del self.plugins[key]

    def has_key(self, k):
        return k in self.plugins

    def update(self, *args, **kwargs):
        return self.plugins.update(*args, **kwargs)

    def keys(self):
        return self.plugins.keys()

    def values(self):
        return self.plugins.values()

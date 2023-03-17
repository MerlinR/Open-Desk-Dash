import importlib
import os
import shutil
import sqlite3
import tarfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Union

import pip
import requests
import toml
from flask import Blueprint, Flask, current_app

from open_desk_dash.lib.db_control import get_config_db
from open_desk_dash.lib.exceptions import DeletionFailed, InstallFailed
from open_desk_dash.lib.plugin_utils import plugin_path

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

    def save_to_db(self):
        try:
            connection = get_config_db()
            cur = connection.cursor()
            sql = f"REPLACE INTO plugins (name, path, title, description, author, github, tag, version, tagName, updated) VALUES (?,?,?,?,?,?,?,?,?,?);"
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
            print(f"Failed to save plugin registry\n{e}")
            connection.rollback()
            raise e
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
                try:
                    self.plugins[registry["name"]].save_to_db()
                except Exception as e:
                    print(f"Failed to register plugin due to..\n{e}")
            self.app.plugin_path = plugin_path

    def import_plugins(self):
        for name, plugin in self.plugins.items():

            plugin_setup, plugin_blueprint = self.import_plugin_module(name, plugin.path)

            if not plugin_blueprint:
                print(f"Skipping {name} Due to no blueprint found")
                continue

            self.app.register_blueprint(plugin_blueprint)

            pages = [
                str(p)
                for p in self.app.url_map.iter_rules()
                if plugin.name in str(p) and "static" not in str(p) and "config" not in str(p)
            ]

            for p in self.app.url_map.iter_rules():
                if plugin.name in str(p) and "config" in str(p):
                    self.plugins[name].config_page = str(p)

            self.plugins[name].pages = pages
            self.plugins[name].setupFn = plugin_setup

    def import_plugin_module(self, module_name: str, path: str) -> Union[Callable, Blueprint]:
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

        if not os.path.exists(registry):
            return None

        config = toml.load(registry)
        config["plugin"]["name"] = name
        config["plugin"]["path"] = path
        return config["plugin"]

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
                self.plugins[plugin["name"]] = Plugin.from_dict(dict(zip(plugin.keys(), plugin)))

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
                    sql = f"DELETE FROM plugins WHERE name = '{row['name']}';"
                    print(sql)
                    cur.execute(sql)
                    connection.commit()
                    self.plugins.pop(row["name"], None)

        except Exception as e:
            print("Failed to load plugin DB")
            print(e)
        finally:
            connection.close()

    def find_plugin_registry(self, repo: str) -> str:
        for file in Path(repo).rglob("registry.toml"):
            return file.as_posix()

    def find_plugin_requirements(self, repo: str) -> str:
        for file in Path(repo).rglob("requirements.txt"):
            return file.as_posix()

    def plugin_install(self, link: str):
        tmp_repo_path = os.path.join(self.plugins_dir, "new_plugin")
        accountName = link.split("/")[-2]
        repoName = link.split("/")[-1]

        release = self.plugin_api_check(accountName, repoName)

        if not release:
            print(f"No release found in Repo")
            raise InstallFailed(
                "Cannot find release info, ensure public github link with a release.",
                msg_type="info",
            )
        elif release.get("message"):
            print(f"Github API limit")
            raise InstallFailed(
                release.get("message"),
                msg_type="info",
            )

        print(f"Installing {repoName} Version {release['tag_name']} - {release['name']}")
        try:
            response = requests.get(release["tarball_url"], stream=True)
            with tarfile.open(fileobj=response.raw, mode=f"r|gz") as tar:
                tar.extractall(path=tmp_repo_path)
        except Exception as e:
            print(f"Failed to download release\n{e}")
            raise InstallFailed(str(e))

        registry_path = os.path.dirname(self.find_plugin_registry(tmp_repo_path))

        if not registry_path:
            print("Failed to Install, cancelling")
            shutil.rmtree(tmp_repo_path)
            raise InstallFailed("Plugin is missing registry toml file, cannot install.")

        pluginName = os.path.basename(registry_path)

        new_plugin_path = os.path.join(self.plugins_dir, f"{accountName}_{pluginName}")

        if os.path.exists(new_plugin_path):
            print("Plugin Already exists, skipping")
            shutil.rmtree(tmp_repo_path)
            raise InstallFailed(
                "Plugin already installed, restart to view or manually delete and retry.",
                msg_type="info",
            )

        os.rename(tmp_repo_path, new_plugin_path)

        registry = self.get_plugin_registry(
            f"{accountName}_{pluginName}",
            os.path.dirname(self.find_plugin_registry(new_plugin_path)),
        )

        registry["tag"] = release["tag_name"]
        registry["tagName"] = release["name"]

        self.plugins[registry["name"]] = Plugin.from_dict(registry)
        try:
            self.plugins[registry["name"]].save_to_db()
        except Exception as e:
            raise InstallFailed(str(e))

        requirements_file = self.find_plugin_requirements(new_plugin_path)
        if requirements_file:
            try:
                self.plugin_requirements_install(requirements_file)
            except Exception as e:
                print(f"Failed to install plugin requirements\n{e}")
                raise InstallFailed(f"Failed to install plugin requirements\n{e}")

    def plugin_requirements_install(self, req_path: str):
        with open(req_path, "r") as req_file:
            for line in req_file:
                package = line.strip()
                print(f"Installing {package}")
                if hasattr(pip, "main"):
                    pip.main(["install", package])
                else:
                    pip._internal.main(["install", package])

    def plugin_delete(self, name: str):
        path = self.find_plugin_root_dir(name)
        if path and os.path.exists(path):
            print("Plugin exists, Deleting")
            try:
                shutil.rmtree(path)
            except Exception as e:
                raise e
        else:
            print("Plugin doesn't exist")
            raise DeletionFailed(msg="Plugin doesn't exist, failed to delete", msg_type="error")

    def plugin_api_check(self, author: str, repo: str):
        git_api_link = GIT_RELEASE_PATH.format(author=author, repo=repo)

        try:
            response = requests.get(git_api_link)
        except requests.exceptions.ConnectionError:
            print("No internet")
            return None

        if response.status_code == 403:
            return response.json()
        elif response.status_code != 200:
            return None
        return response.json()

    def update_plugin_check(self):
        for name, plugin in self.plugins.items():
            if name in self.app.config["def_plugins"]:
                continue
            print(f"Checking {name} for updates")
            accountName = plugin.github.split("/")[-2]
            repoName = plugin.github.split("/")[-1]

            release = self.plugin_api_check(accountName, repoName)
            if not release:
                print(f"{name} has no releases")
                continue
            elif release.get("message"):
                print(f"Reached github API limit")
                continue

            if release["tag_name"] != plugin.tag and self.app.config["config"].auto_update_plugins:
                print("Out of Date, Auto Updating")
                self.update_plugin(plugin.name)
            elif (
                release["tag_name"] != plugin.tag
                and not self.app.config["config"].auto_update_plugins
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

    def __setitem__(self, key, item):
        self.plugins[key] = item

    def __getitem__(self, key):
        return self.plugins[key]

    def __repr__(self):
        return repr(self.plugins)

    def __len__(self):
        return len(self.plugins)

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

    def items(self):
        return self.plugins.items()

    def pop(self, *args):
        return self.plugins.pop(*args)

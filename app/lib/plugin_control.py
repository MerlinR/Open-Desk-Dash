import importlib
import os
import sqlite3
from pathlib import Path
from typing import Dict

import git
import toml
from app.lib.db_control import get_config_db
from flask import Blueprint, Flask


class pluginManager:
    def __init__(self, app: Flask, plugins_dir=str):
        self.app = app
        self.plugins_dir = plugins_dir
        self.plugins = {}
        self.load_plugins_from_DB()
        self.import_plugins()
        self.load_plugins()

    def load_plugins_from_DB(self):
        try:
            connection = get_config_db()
            connection.row_factory = sqlite3.Row
            cur = connection.cursor()

            sql = f"SELECT * FROM plugins"
            cur.execute(sql)
            existing = cur.fetchall()
            for plugin in existing:
                self.plugins[plugin["name"]] = dict(zip(plugin.keys(), plugin))

            for name, data in self.plugins.copy().items():
                if not os.path.exists(data["path"]):
                    print(f"Module {name} Missing... Deleting SQL record")
                    sql = f"DELETE FROM plugins WHERE id = {data['id']};"
                    cur.execute(sql)
                    connection.commit()
                    self.plugins.pop(name)

        except Exception as e:
            print("Failed to load plugin DB")
            print(e)
        finally:
            connection.close()

    def import_plugins(self):
        for name, path in self.plugin_list().items():
            registry = self.get_plugin_registry(name, path)
            if not registry:
                print(f"Unknown {name} Plugin has no registry File. Skipping")
                continue
            elif registry["name"] not in self.plugins.keys():
                self.save_plugin_register(registry)

            plugin_import = self.load_plugin_module(registry["name"], path)
            if not plugin_import:
                print(f"Skipping {name} [{registry['name']}] Due to import failure")
                continue

            self.plugins[name] = {
                **self.plugins[name],
                "path": path,
                "setup": plugin_import[0],
                "blueprint": plugin_import[1],
            }

    def load_plugin_module(self, module_name: str, path: str) -> Blueprint:
        path = path.replace("/", ".")
        try:
            plugin_api = importlib.import_module(f".{module_name}", path).api
            try:
                plugin_setup = importlib.import_module(f".{module_name}", path).setup
            except AttributeError:
                print(f"{module_name} has no setup function")
                plugin_setup = None
            plugin_api.static_folder = "./src/static"
            plugin_api.template_folder = "./src"
            plugin_api.url_prefix = f"/{module_name}"
        except ModuleNotFoundError as e:
            print(f"Failed to import {module_name}")
            print(e)
            return None

        return plugin_setup, plugin_api

    def load_plugins(self):
        for name, data in self.plugins.items():
            self.app.register_blueprint(data["blueprint"])

            pages = [
                str(p)
                for p in self.app.url_map.iter_rules()
                if data["name"] in str(p)
                and "static" not in str(p)
                and "config" not in str(p)
            ]

            self.plugins[name]["config_page"] = None
            for p in self.app.url_map.iter_rules():
                if data["name"] in str(p) and "config" in str(p):
                    self.plugins[name]["config_page"] = str(p)

            self.plugins[name]["pages"] = pages

    def save_plugin_register(self, registry: dict):
        try:
            connection = get_config_db()
            cur = connection.cursor()
            sql = f"INSERT INTO plugins (name, path, title, description, author, github, autoUpdate, tag, version) "
            sql += f"VALUES('{registry['name']}', '{registry['path']}', '{registry['title']}', '{registry['description']}', '{registry['author']}', '{registry['github']}', 1, '{registry['tag']}','{registry['version']}');"
            cur.execute(sql)
            connection.commit()
        except Exception as e:
            print("Failed to save plugin registry")
            print(e)
            connection.rollback()
        finally:
            self.plugins[registry["name"]] = registry
            connection.close()

    def run_plugins_setup(self):
        for plugin in self.plugins.values():
            if plugin.get("setup"):
                plugin["setup"](self.app)

    def plugin_list(self) -> dict:
        plugins = {}
        for dir in os.listdir(self.plugins_dir):
            if os.path.isdir(os.path.join(self.plugins_dir, dir)) and dir[0] != "_":
                for file in Path(os.path.join(self.plugins_dir, dir)).rglob(
                    "registry.toml"
                ):
                    plugins[os.path.basename(os.path.dirname(file))] = os.path.dirname(
                        file
                    )
        return plugins

    def find_registry(self, repo: str) -> str:
        for file in Path(repo).rglob("registry.toml"):
            return file.as_posix()

    def get_plugin_registry(self, name: str, path: str) -> dict:
        registry = os.path.join(path, "registry.toml")
        if os.path.exists(registry):
            config = toml.load(registry)
            config["plugin"]["name"] = name
            config["plugin"]["path"] = path
            return config["plugin"]
        return None

    def plugin_install(self, link: str):
        tmp_repo_path = os.path.join(self.plugins_dir, "new_repo")
        git.Repo.clone_from(link, tmp_repo_path)

        accountName = link.split("/")[-2]
        registry_path = self.find_registry(tmp_repo_path)
        pluginName = os.path.basename(os.path.dirname(registry_path))

        new_plugin_path = os.path.join(self.plugins_dir, f"{accountName}_{pluginName}")
        os.rename(tmp_repo_path, new_plugin_path)

    # def plugin_delete(self, name: str):
    #     print("Deleting")

    # def plugin_version_check(self, name: str):
    #     print("Version Check")

    # def plugin_update(self, name: str):
    #     print("Updating")

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

import importlib
import sqlite3
from os import listdir, path
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
        except Exception as e:
            print("Failed to load plugin DB")
            print(e)
        finally:
            connection.close()

    def import_plugins(self) -> Dict[str, Blueprint]:
        for name, path in self.plugin_list().items():
            registry = self.get_plugin_registry(name)
            if not registry:
                print(f"Unknown {name} Plugin has no registry File. Skipping")
                continue

            if registry["name"] not in self.plugins.keys():
                self.save_plugin_register(registry)

            plugin_import = self.load_plugin_module(
                registry["name"], registry["direct_name"]
            )
            if not plugin_import:
                print(f"Skipping {name} [{registry['name']}] Due to import failure")
                continue

            self.plugins[name] = {
                **self.plugins[name],
                "path": path,
                "setup": plugin_import[0],
                "blueprint": plugin_import[1],
            }

    def load_plugin_module(self, module_name: str, registry_name: str) -> Blueprint:
        try:
            plugin_api = importlib.import_module(
                f".{registry_name}", f"plugins.{module_name}"
            ).api
            try:
                plugin_setup = importlib.import_module(
                    f".{registry_name}", f"plugins.{module_name}"
                ).setup
            except AttributeError:
                print(f"{module_name} has no setup function")
                plugin_setup = None
            plugin_api.static_folder = "./src/static"
            plugin_api.template_folder = "./src"
            plugin_api.url_prefix = f"/{module_name}"
        except ModuleNotFoundError as e:
            print(f"Failed to import {module_name}")
            return None

        return plugin_setup, plugin_api

    def load_plugins(self) -> list:
        for plugin, data in self.plugins.items():
            self.app.register_blueprint(data["blueprint"])

            pages = [
                str(p)
                for p in self.app.url_map.iter_rules()
                if data["name"] in str(p)
                and "static" not in str(p)
                and "config" not in str(p)
            ]

            self.plugins[plugin]["config_page"] = None
            for p in self.app.url_map.iter_rules():
                if data["name"] in str(p) and "config" in str(p):
                    self.plugins[plugin]["config_page"] = str(p)

            self.plugins[plugin]["pages"] = pages

    def save_plugin_register(self, registry: dict):
        try:
            connection = get_config_db()
            cur = connection.cursor()
            sql = f"INSERT INTO plugins (name, title, description, author, github, autoUpdate, tag, version) "
            sql += f"VALUES('{registry['name']}', '{registry['title']}', '{registry['description']}', '{registry['author']}', '{registry['github']}', 1, '{registry['tag']}','{registry['version']}');"
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
        for f in listdir(self.plugins_dir):
            if path.isdir(path.join(self.plugins_dir, f)) and f[0] != "_":
                if path.join(path.join(self.plugins_dir, f), f.split("_")[-1]):
                    plugins[f] = path.join(self.plugins_dir, f)
        return plugins

    def get_plugin_registry(self, name: str) -> dict:
        registry = path.join(self.plugins_dir, name, "registry.toml")
        if path.exists(registry):
            config = toml.load(registry)
            config["plugin"]["name"] = name
            config["plugin"]["direct_name"] = name.split("_")[-1]
            return config["plugin"]

    # def plugin_install(self, link: str):
    #     print("Installing")

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

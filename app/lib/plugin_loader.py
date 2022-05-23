import importlib
from os import listdir, path
from typing import Dict

import toml
from flask import Blueprint, Flask

PLUGIN_DIR = "plugins"


def plugin_list() -> list:
    plugins = []
    for f in listdir(PLUGIN_DIR):
        if path.isdir(path.join(PLUGIN_DIR, f)) and f[0] != "_":
            if path.join(path.join(PLUGIN_DIR, f), f.split("_")[-1]):
                plugins.append(f)
    return plugins


def get_plugin_path(name: str) -> str:
    for plugin in listdir(PLUGIN_DIR):
        if path.isdir(path.join(PLUGIN_DIR, plugin)) and plugin == name:
            return path.join(PLUGIN_DIR, plugin, f"{plugin.split('_')[-1]}.py")


def get_plugin_registry(name: str) -> dict:
    registry = path.join(PLUGIN_DIR, name, "registry.toml")
    if path.exists(registry):
        config = toml.load(registry)
        config["plugin"]["name"] = name
        config["plugin"]["direct_name"] = name.split("_")[-1]
        return config["plugin"]


def import_blueprint(module_name: str, registry_name: str) -> Blueprint:
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
        plugin_api.template_folder = "./src/templates"
        plugin_api.url_prefix = f"/{module_name}"
    except ModuleNotFoundError as e:
        print(f"Failed to import {module_name}")
        return None

    return plugin_setup, plugin_api


def import_plugins() -> Dict[str, Blueprint]:
    plugins = {}
    for plugin in plugin_list():
        registry = get_plugin_registry(plugin)
        if not registry:
            print(f"Unknown {plugin} Plugin has no registry File. Skipping")
            continue

        plugin_import = import_blueprint(registry["name"], registry["direct_name"])
        if not plugin_import:
            print(f"Skipping {plugin} [{registry['name']}] Due to import failure")
            continue
        plugins[plugin] = {
            "name": registry["name"],
            "path": get_plugin_path(plugin),
            "setup": plugin_import[0],
            "blueprint": plugin_import[1],
        }

    return plugins


def load_plugins(app: Flask) -> list:
    app.config["plugins"] = {}
    app.config["pages"] = []

    for plugin, data in import_plugins().items():
        app.config["plugins"][plugin] = data

        if data["setup"]:
            data["setup"](app)

        app.register_blueprint(data["blueprint"])

        app.config["pages"] += [
            str(p)
            for p in app.url_map.iter_rules()
            if data["name"] in str(p)
            and "static" not in str(p)
            and "config" not in str(p)
        ]

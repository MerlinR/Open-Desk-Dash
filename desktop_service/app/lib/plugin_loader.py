from genericpath import isdir
import importlib
from os import listdir
from os.path import join


def plugin_list() -> list:
    plugins = [
        f for f in listdir("./plugins") if isdir(join("./plugins", f)) and f[0] != "_"
    ]
    return plugins


def import_blueprint_plugins():
    plugins = []
    for plugin in plugin_list():
        try:
            plugins.append(
                importlib.import_module(f".{plugin}", f"plugins.{plugin}").api
            )
        except ModuleNotFoundError as e:
            print(f"Failed to import {plugin}")
    return plugins

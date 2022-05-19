from genericpath import isdir
import importlib
from os import listdir
from os.path import isfile, join


def plugin_list() -> list:
    plugins = [
        f for f in listdir("./plugins") if isdir(join("./plugins", f)) and f[0] != "_"
    ]
    return plugins


def import_blueprint_plugins():
    plugins = [
        importlib.import_module(f".{plugin}", f"plugins.{plugin}").api
        for plugin in plugin_list()
    ]
    return plugins

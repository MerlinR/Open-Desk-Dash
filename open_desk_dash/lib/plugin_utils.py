import inspect

from flask import current_app, request


def plugin_path() -> str:
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            return plugins.path
    if not name:
        print("No DB found")
        return


def plugin_config(config_name: str) -> str:
    for plugin in current_app.config["plugins"].keys():
        if plugin == request.blueprint:
            return current_app.config[plugin].get(config_name)

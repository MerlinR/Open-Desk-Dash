import inspect

from flask import current_app


def get_my_path():
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            return plugins.path
    if not name:
        print("No DB name to create")
        return

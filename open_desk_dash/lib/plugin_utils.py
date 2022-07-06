from flask import current_app, request


def plugin_path() -> str:
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    plugin_name = request.blueprint
    return current_app.config["plugins"][plugin_name].path


def plugin_config(config_name: str) -> str:
    return current_app.config.get(request.blueprint, {}).get(config_name)

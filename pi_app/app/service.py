from flask import Flask

from app.lib.dashboard import home_api
from app.lib.plugin_loader import import_blueprint_plugins

app = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)


# app.config.from_object("config.config.Config")

app.register_blueprint(home_api)

for plugin in import_blueprint_plugins():
    app.register_blueprint(plugin)

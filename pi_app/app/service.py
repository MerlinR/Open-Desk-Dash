from flask import Flask

from app.lib.plugin_loader import import_blueprint_plugins

app = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)

app.config.from_object("configs.config.Config")

for plugin in import_blueprint_plugins():
    app.register_blueprint(plugin)

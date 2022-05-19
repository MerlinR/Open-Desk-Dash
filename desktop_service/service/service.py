from flask import Flask, g, request

from lib.system import sys_api
from plugin_loader import import_blueprint_plugins


app = Flask("OpenDeskDash")

for plugin in import_blueprint_plugins():
    app.register_blueprint(plugin)

app.register_blueprint(sys_api)

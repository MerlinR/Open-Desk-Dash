from flask import Flask, jsonify, request

from lib.system import sys_api
from lib.api.cfg_api import cfg_api
from app.lib.plugin_loader import import_blueprint_plugins


app = Flask("OpenDeskDash")

app.config.from_object("config.config.Config")

for plugin in import_blueprint_plugins():
    app.register_blueprint(plugin)

app.register_blueprint(sys_api)
app.register_blueprint(cfg_api)


@app.before_request
def before_request():
    auth = request.headers.get("X-Authentication")
    if auth != app.secret_key and request.remote_addr != "127.0.0.1":
        return jsonify({"message": "ERROR: Unauthorized"}), 401

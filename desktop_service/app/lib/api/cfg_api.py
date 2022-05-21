from app.lib.plugin_loader import plugin_list
from flask import Blueprint, current_app, jsonify

cfg_api = Blueprint("cfg", __name__, url_prefix="/api")


@cfg_api.route("/key", methods=["GET"])
def get_key():
    return (jsonify(current_app.secret_key), 200)


@cfg_api.route("/plugins", methods=["GET"])
def pluginList():
    return (jsonify(plugin_list()), 200)

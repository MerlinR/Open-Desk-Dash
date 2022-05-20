from flask import Blueprint, jsonify
from config.config import load_secret_key
from app.lib.plugin_loader import plugin_list

cfg_api = Blueprint("cfg", __name__, url_prefix="/api")


@cfg_api.route("/key", methods=["GET"])
def get_key():
    return (jsonify(load_secret_key()), 200)


@cfg_api.route("/plugins", methods=["GET"])
def pluginList():
    return (jsonify(plugin_list()), 200)

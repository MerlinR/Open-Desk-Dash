from flask import Flask, redirect, request
from werkzeug.urls import url_parse

from open_desk_dash.config import cfg_api
from open_desk_dash.lib.db_control import setup_DB_control
from open_desk_dash.lib.plugin_control import pluginManager

ODDash = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)
PLUGIN_DIR = "plugins"

ODDash.config.from_object("configs.config.Config")
ODDash.register_blueprint(cfg_api)
ODDash.config["path_to_name"] = {}

with ODDash.app_context():
    setup_DB_control()
    ODDash.config["plugins"] = pluginManager(ODDash, PLUGIN_DIR)
    ODDash.config["plugins"].run_plugins_setup()


@ODDash.route("/", methods=["GET"])
def home():
    return redirect(ODDash.config["config"]["pages"][0])


@ODDash.errorhandler(404)
def page_not_found(e):
    return redirect(ODDash.config["config"]["pages"][0])


@ODDash.route("/next", methods=["GET"])
def next_dash():
    prev_page = url_parse(request.referrer)
    try:
        indx = ODDash.config["config"]["pages"].index(prev_page.path)
        indx += 1
        if indx == len(ODDash.config["config"]["pages"]):
            indx = 0
    except IndexError:
        indx = 0
    return redirect(ODDash.config["config"]["pages"][indx])


@ODDash.route("/prev", methods=["GET"])
def prev_dash():
    try:
        prev_page = url_parse(request.referrer)
        indx = ODDash.config["config"]["pages"].index(prev_page.path)
        indx -= 1
        if indx < 0:
            indx = len(ODDash.config["config"]["pages"]) - 1
    except IndexError:
        indx = 0
    return redirect(ODDash.config["config"]["pages"][indx])

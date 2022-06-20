from flask import Flask, redirect, request
from werkzeug.urls import url_parse

from open_desk_dash.config import cfg_api
from open_desk_dash.lib.db_control import setup_DB_control
from open_desk_dash.lib.plugin_control import PluginManager
from open_desk_dash.lib.plugin_utils import plugin_config
from open_desk_dash.lib.update_control import update_check

ODDash = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)
ODDash.jinja_env.globals["plugin_config"] = plugin_config

ODDash.config.from_object("configs.config.Config")
ODDash.register_blueprint(cfg_api)
ODDash.config["def_plugins"] = [
    "default_dashboard",
    "default_weather",
    "rss_dash",
    "external_dash",
]

with ODDash.app_context():
    setup_DB_control()
    update_check()
    ODDash.config["plugins"] = PluginManager(ODDash, "plugins")
    ODDash.config["plugins"].register_plugins()
    ODDash.config["plugins"].update_plugin_check()
    ODDash.config["plugins"].import_plugins()
    ODDash.config["plugins"].run_plugins_setup()


@ODDash.route("/", methods=["GET"])
def home():
    return redirect(ODDash.config["config"]["pages"][0])


@ODDash.errorhandler(404)
def page_not_found(e):
    return redirect(ODDash.config["config"]["pages"][0])


def fuzzy_index(srch: str, extra: str, within: list) -> int:
    if extra:
        srch = f"{srch}?{extra}"
    for i, page in enumerate(within):
        if srch in page:
            return i
    return 0


@ODDash.route("/next", methods=["GET"])
def next_dash():
    prev_page = url_parse(request.referrer)
    indx = fuzzy_index(
        prev_page.path, prev_page.query, ODDash.config["config"]["pages"]
    )
    indx += 1
    if indx == len(ODDash.config["config"]["pages"]):
        indx = 0
    return redirect(ODDash.config["config"]["pages"][indx])


@ODDash.route("/prev", methods=["GET"])
def prev_dash():
    prev_page = url_parse(request.referrer)
    indx = fuzzy_index(
        prev_page.path, prev_page.query, ODDash.config["config"]["pages"]
    )
    indx -= 1
    if indx < 0:
        indx = len(ODDash.config["config"]["pages"]) - 1
    return redirect(ODDash.config["config"]["pages"][indx])

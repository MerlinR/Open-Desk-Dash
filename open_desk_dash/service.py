from flask import Flask, redirect, request
from werkzeug.urls import url_parse

from open_desk_dash.config import cfg_api
from open_desk_dash.lib.db_controls import setup_DB_control
from open_desk_dash.lib.plugin_control import PluginManager
from open_desk_dash.lib.plugin_utils import plugin_config

ODDash = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)
ODDash.jinja_env.globals["plugin_config"] = plugin_config

ODDash.config.from_object("configs.Config")
ODDash.register_blueprint(cfg_api)
ODDash.config["def_plugins"] = [
    "default_dashboard",
    "default_weather",
    "rss_dash",
    "external_dash",
]

with ODDash.app_context():
    setup_DB_control()
    ODDash.config["oddash"].update_check()
    ODDash.config["plugins"] = PluginManager(ODDash, "ext_plugins")
    ODDash.config["plugins"].run_plugins_setup()


@ODDash.route("/", methods=["GET"])
def home():
    return redirect(ODDash.config["oddash"].pages[0])


@ODDash.errorhandler(404)
def page_not_found(e):
    return redirect(ODDash.config["oddash"].pages[0])


def fuzzy_index(srch: str, extra: str, within: list) -> int:
    if extra:
        srch = f"{srch}?{extra}"
    for i, page in enumerate(within):
        if srch in page:
            return i
    return 0


def find_next_page(request, forward: bool) -> str:
    try:
        prev_page = url_parse(request.referrer)
    except AttributeError:
        return redirect(ODDash.config["oddash"].pages[0])
    indx = fuzzy_index(prev_page.path, prev_page.query, ODDash.config["oddash"].pages)
    if forward:
        indx = 0 if indx == len(ODDash.config["oddash"].pages) - 1 else indx + 1
    else:
        indx = len(ODDash.config["oddash"].pages) - 1 if indx < 0 else indx - 1
    return ODDash.config["oddash"].pages[indx]


@ODDash.route("/next", methods=["GET"])
def next_dash():
    return redirect(find_next_page(request, True))


@ODDash.route("/prev", methods=["GET"])
def prev_dash():
    return redirect(find_next_page(request, False))

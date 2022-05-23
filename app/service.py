from flask import Flask, redirect, request
from werkzeug.urls import url_parse

from app.config import cfg_api
from app.lib.db_control import setup_DB_control
from app.lib.plugin_loader import load_plugins

app = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)

app.config.from_object("configs.config.Config")
app.register_blueprint(cfg_api)
app.config["path_to_name"] = {}

with app.app_context():
    setup_DB_control()

load_plugins(app)


@app.route("/", methods=["GET"])
def home():
    return redirect(app.config["pages"][0])


@app.route("/next", methods=["GET"])
def next_dash():
    prev_page = url_parse(request.referrer)
    try:
        indx = app.config["pages"].index(prev_page.path)
        indx += 1
        if indx == len(app.config["pages"]):
            indx = 0
    except IndexError:
        indx = 0
    return redirect(app.config["pages"][indx])


@app.route("/prev", methods=["GET"])
def prev_dash():
    try:
        prev_page = url_parse(request.referrer)
        indx = app.config["pages"].index(prev_page.path)
        indx -= 1
        if indx < 0:
            indx = len(app.config["pages"]) - 1
    except IndexError:
        indx = 0
    return redirect(app.config["pages"][indx])

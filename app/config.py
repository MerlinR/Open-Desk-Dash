from flask import Blueprint, jsonify, render_template, request

cfg_api = Blueprint(
    "config",
    __name__,
    url_prefix="/configure/",
)


@cfg_api.route("/", methods=["GET"])
def config():
    return render_template("config.html")


@cfg_api.route("/plugins", methods=["GET"])
def plugins():
    return render_template("plugins.html")

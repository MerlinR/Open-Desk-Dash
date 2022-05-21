from flask import Blueprint, jsonify, render_template, request

home_api = Blueprint("home", __name__, url_prefix="/")


@home_api.route("/", methods=["GET"])
def dashboard():
    return render_template("index.html")

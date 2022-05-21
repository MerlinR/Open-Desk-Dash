from flask import Blueprint, jsonify, render_template, request

api = Blueprint(
    "dashboard",
    __name__,
    static_folder="./src/static",
    template_folder="./src/templates",
    static_url_path="/static/def.dashboard/",
    url_prefix="/",
)


@api.route("/", methods=["GET"])
def dashboard():
    return render_template("def_dashboard.html")

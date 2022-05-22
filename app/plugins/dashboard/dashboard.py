from flask import Blueprint, render_template

api = Blueprint(
    "dashboard",
    __name__,
    static_folder="./src/static",
    template_folder="./src/templates",
    static_url_path="/static/def.dashboard/",
    url_prefix="/",
)


@api.route("/def.dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")
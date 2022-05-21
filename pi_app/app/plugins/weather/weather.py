from flask import Blueprint, jsonify, render_template, request

api = Blueprint(
    "weather",
    __name__,
    static_folder="./src/static",
    template_folder="./src/templates",
    static_url_path="/static/def.weather/",
    url_prefix="/weather",
)


@api.route("/", methods=["GET"])
def dashboard():
    return render_template("weather.html")

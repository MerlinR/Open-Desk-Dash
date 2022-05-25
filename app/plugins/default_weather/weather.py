from flask import Blueprint, render_template

api = Blueprint("default_weather", __name__)


@api.route("/", methods=["GET"])
def weather():
    return render_template("default_weather/weather.html")

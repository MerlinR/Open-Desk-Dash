from flask import Blueprint, render_template

api = Blueprint("weather", __name__)


@api.route("/", methods=["GET"])
def weather():
    return render_template("weather.html")

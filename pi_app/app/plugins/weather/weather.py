from flask import Blueprint, render_template

api = Blueprint(
    "weather",
    __name__,
    static_folder="./src/static",
    template_folder="./src/templates",
    static_url_path="/static/def.weather/",
    url_prefix="/",
)


@api.route("/def.weather", methods=["GET"])
def weather():
    return render_template("weather.html")

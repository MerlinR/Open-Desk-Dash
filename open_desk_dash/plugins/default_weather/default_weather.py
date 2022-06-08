from flask import Blueprint, Flask, current_app, render_template, request

api = Blueprint("default_weather", __name__)


def setup(app: Flask):
    with app.app_context():
        current_app.create_config(
            {
                "location": str,
            },
            {
                "location": "London",
            },
        )


@api.route("/", methods=["GET"])
def weather():
    return render_template("default_weather/weather.html")


@api.route("/config", methods=["GET", "POST"])
def weather_config():
    extra = {"msg": "", "type": ""}
    if request.method == "POST":
        try:
            current_app.save_config(
                {
                    "location": request.form["location"],
                }
            )
            extra["msg"] = "Saved"
        except Exception as e:
            print(f"Failed to save config, {e}")
            extra = {"msg": f"Failed, {e}", "type": "error"}

    return render_template(
        "default_weather/config.html", msg=extra["msg"], msg_type=extra["type"]
    )

from flask import Blueprint, Flask, current_app, render_template, request

api = Blueprint("default_dashboard", __name__)


def setup(app: Flask):
    with app.app_context():
        current_app.create_config(
            {
                "title": int,
                "imageLink": str,
            },
            {
                "title": "Open Desk Dash",
                "imageLink": "https://giffiles.alphacoders.com/209/209343.gif",
            },
        )


@api.route("/", methods=["GET"])
def dashboard():
    return render_template("default_dashboard/dashboard.html")


@api.route("/config", methods=["GET", "POST"])
def dashboard_config():
    if request.method == "POST":
        try:
            new_title = request.form["dash_title"]
            new_image = request.form["dash_image"]
            current_app.save_config(
                {
                    "title": new_title,
                    "imageLink": new_image,
                }
            )

        except Exception as e:
            print("Failed to save config")
            print(e)
    return render_template("default_dashboard/config.html")

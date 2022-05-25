from flask import Blueprint, Flask, current_app, render_template

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
    return render_template("default_dashboard/config.html")

from flask import Blueprint, Flask, current_app, g, render_template

api = Blueprint("dashboard", __name__)


def setup(app: Flask):
    with app.app_context():
        current_app.create_db()


@api.route("/", methods=["GET"])
def dashboard():
    print(current_app.connect_db())
    return render_template("dashboard.html")

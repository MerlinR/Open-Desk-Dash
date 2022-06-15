import requests
from flask import Blueprint, render_template, request

api = Blueprint("external_dash", __name__)


@api.route("/", methods=["GET"])
def external_dash():
    link = request.args.get("link", default="", type=str)
    if not link:
        return render_template("external_dash/external_dash.html", content="Unknown")

    page = requests.get(link)
    if page.status_code != 200:
        return render_template("external_dash/external_dash.html", content="error")

    return render_template(
        "external_dash/external_dash.html", content=page.content.decode()
    )

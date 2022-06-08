from flask import Blueprint, Flask, current_app, render_template, request

api = Blueprint("default_dashboard", __name__)


def setup(app: Flask):
    with app.app_context():
        current_app.create_config(
            {
                "title": int,
                "imageLink": str,
                "textColor": str,
            },
            {
                "title": "Open Desk Dash",
                "imageLink": "https://giffiles.alphacoders.com/209/209343.gif",
                "textColor": "#22262e",
            },
        )


@api.route("/", methods=["GET"])
def dashboard():
    return render_template("default_dashboard/dashboard.html")


@api.route("/config", methods=["GET", "POST"])
def dashboard_config():
    extra = {"msg": "", "type": ""}
    if request.method == "POST":
        try:
            current_app.save_config(
                {
                    "title": request.form["dash_title"],
                    "imageLink": request.form["dash_image"],
                    "textColor": request.form["text_color"],
                }
            )
            extra["msg"] = "Saved"
        except Exception as e:
            print(f"Failed to save config, {e}")
            extra = {"msg": f"Failed, {e}", "type": "error"}

    return render_template(
        "default_dashboard/config.html", msg=extra["msg"], msg_type=extra["type"]
    )

from flask import Blueprint, current_app, redirect, render_template, request

from lib.db_control import gather_config_db, get_config_db

cfg_api = Blueprint(
    "config",
    __name__,
    url_prefix="/config/",
)


@cfg_api.route("/", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        try:
            transition_speed = request.form["transition"]
            page_order = request.form["page_order"]
            connection = get_config_db()

            cur = connection.cursor()
            cur.execute(
                "UPDATE config SET transition = ?, pages = ? WHERE id = 1 ",
                (transition_speed, page_order),
            )

            connection.commit()
        except Exception as e:
            print("Failed to save config")
            print(e)
            connection.rollback()
        finally:
            gather_config_db()
            connection.close()

    return render_template("config.html")


@cfg_api.route("/<plugin>")
def plugin_config(plugin):
    if current_app.config["plugins"][plugin]["config_page"]:
        return redirect(current_app.config["plugins"][plugin]["config_page"])
    else:
        return redirect("/config/")


@cfg_api.route("/plugins", methods=["GET"])
def plugins():
    return render_template("plugins.html")

from flask import Blueprint, current_app, redirect, render_template, request

from open_desk_dash.lib.db_control import gather_config_db, get_config_db

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
            autoUpdate = None
            if request.form.get("autoUpdate"):
                autoUpdate = True
            else:
                autoUpdate = False

            autoUpdatePlugins = None
            if request.form.get("autoUpdatePlugins"):
                autoUpdatePlugins = True
            else:
                autoUpdatePlugins = False

            connection = get_config_db()

            cur = connection.cursor()
            cur.execute(
                "UPDATE config SET transition = ?, pages = ?, autoUpdate = ?, autoUpdatePlugins = ? WHERE id = 1 ",
                (transition_speed, page_order, autoUpdate, autoUpdatePlugins),
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
    if current_app.config["plugins"].plugins[plugin]["config_page"]:
        return redirect(current_app.config["plugins"].plugins[plugin]["config_page"])
    else:
        return redirect("/config/")


@cfg_api.route("/plugins", methods=["GET", "POST"])
def plugins():
    if request.method == "POST":
        link = request.form["github_link"]
        current_app.config["plugins"].plugin_install(link)
    return render_template("plugins.html")


@cfg_api.route("/delete/<plugin>", methods=["GET"])
def delete_plugin(plugin):
    current_app.config["plugins"].plugin_delete(plugin)
    return redirect("/config/plugins")

from flask import Blueprint, current_app, redirect, render_template, request

from open_desk_dash.lib.db_control import gather_config_db, get_config_db
from open_desk_dash.lib.exceptions import DeletionFailed, InstallFailed

cfg_api = Blueprint(
    "config",
    __name__,
    url_prefix="/config/",
)


@cfg_api.route("/", methods=["GET", "POST"])
def config():
    rtn_msg = {"msg": "", "type": ""}

    if request.method == "POST":
        try:
            transition_speed = request.form["transition"]

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

            selected_pages = request.form.getlist("pages")
            selected_pages_vars = request.form.getlist("pages_vars")
            page_order = []
            for i, page in enumerate(selected_pages):
                if selected_pages_vars[i]:
                    page_order.append(f"{page}?{selected_pages_vars[i]}")
                else:
                    page_order.append(page)
            connection = get_config_db()

            cur = connection.cursor()
            cur.execute(
                "UPDATE config SET transition = ?, pages = ?, autoUpdate = ?, autoUpdatePlugins = ? WHERE id = 1 ",
                (transition_speed, ",".join(page_order), autoUpdate, autoUpdatePlugins),
            )
            connection.commit()
            rtn_msg = {"msg": "Saved", "type": "positive"}
        except Exception as e:
            print(f"Failed to save config. {e}")
            rtn_msg = {"msg": f"Failed to save config, {e}", "type": "error"}
            connection.rollback()
        finally:
            gather_config_db()
            connection.close()

    pages = [page.split("?")[0] for page in current_app.config["config"]["pages"]]
    page_vars = []
    for page in current_app.config["config"]["pages"]:
        if "?" in page:
            page_vars.append(page.split("?")[-1])
        else:
            page_vars.append("")

    return render_template(
        "config.html",
        pages=pages,
        page_vars=page_vars,
        msg=rtn_msg["msg"],
        msg_type=rtn_msg["type"],
    )


@cfg_api.route("/<plugin>")
def plugin_config(plugin):
    if (
        current_app.config["plugins"].plugins.get(plugin)
        and current_app.config["plugins"].plugins[plugin].config_page
    ):
        return redirect(current_app.config["plugins"].plugins[plugin].config_page)
    else:
        return render_template(
            "plugins.html", msg=f"{plugin} has no config options", msg_type="info"
        )


@cfg_api.route("/plugins", methods=["GET", "POST"])
def plugins():
    if request.method == "POST":
        link = request.form.get("github_link")
        if link:
            try:
                current_app.config["plugins"].plugin_install(link)
            except InstallFailed as e:
                return render_template("plugins.html", msg=e, msg_type=e.msg_type)
            except Exception as e:
                print(f"Plugin Install failed {e}")
                return render_template("plugins.html", msg=e, msg_type="error")
        else:
            return render_template(
                "plugins.html", msg="Github link Required", msg_type="info"
            )
    return render_template("plugins.html")


@cfg_api.route("/delete/<plugin>", methods=["GET"])
def delete_plugin(plugin):
    try:
        current_app.config["plugins"].plugin_delete(plugin)
    except DeletionFailed as e:
        return render_template("plugins.html", msg=e, msg_type=e.msg_type)
    except Exception as e:
        print(f"Plugin deletion failed\n{e}")
        return render_template("plugins.html", msg=e, msg_type="error")

    return render_template(
        "plugins.html", msg="Plugin deleted, restart required.", msg_type="info"
    )


@cfg_api.route("/update/<plugin>", methods=["GET"])
def update_plugin(plugin):
    try:
        current_app.config["plugins"].update_plugin(plugin)
    except DeletionFailed as e:
        return render_template("plugins.html", msg=e, msg_type=e.msg_type)
    except InstallFailed as e:
        return render_template("plugins.html", msg=e, msg_type=e.msg_type)
    except Exception as e:
        print(f"Plugin update failed {e}")
        return render_template("plugins.html", msg=e, msg_type="error")
    return render_template(
        "plugins.html", msg="Plugin Updated, restart required.", msg_type="info"
    )

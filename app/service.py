from flask import Flask, redirect, render_template, request, url_for

from app.lib.plugin_loader import import_blueprint_plugins

app = Flask(
    "OpenDeskDash",
    template_folder="./src/templates",
    static_folder="./src/static",
)

rotate_pages = ["def.dashboard", "def.weather"]

app.config.from_object("configs.config.Config")

for plugin in import_blueprint_plugins():
    app.register_blueprint(plugin)


@app.route("/next", methods=["GET"])
def next_dash():
    prev_page = request.referrer
    indx = rotate_pages.index(prev_page.split("/")[-1])
    indx += 1
    if indx == len(rotate_pages):
        indx = 0
    return redirect(rotate_pages[indx])


@app.route("/prev", methods=["GET"])
def prev_dash():
    prev_page = request.referrer
    indx = rotate_pages.index(prev_page.split("/")[-1])
    indx -= 1
    if indx < 0:
        indx = len(rotate_pages) - 1
    return redirect(rotate_pages[indx])

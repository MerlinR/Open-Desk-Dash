from flask import Flask, g, request

from lib.system import sys_api


app = Flask("OpenDeskDash")


app.register_blueprint(sys_api)


if __name__ == "__main__":
    app.run(debug=False)

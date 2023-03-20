import os
import subprocess

from flask import current_app


def restart_oddash():
    if current_app.config["EXPECTED_HOME"] not in os.path.realpath(__file__):
        subprocess.call(["systemctl", "restart", current_app.config["SERVICE_NAME"]])

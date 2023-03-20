import os
import sqlite3
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from datetime import datetime
from tempfile import TemporaryDirectory

import requests
from flask import current_app

from open_desk_dash.lib.misc import restart_oddash

GIT_RELEASE_PATH = "https://api.github.com/repos/{author}/{repo}/releases/latest"


@dataclass
class ODDash:
    def __init__(
        self,
        transition: int,
        pages: str,
        auto_update: bool,
        auto_update_plugins: bool,
        theme: str,
        github: str,
        version: str,
        version_name: str,
        installed: datetime,
        updated: datetime,
    ):
        self.transition = transition
        self.pages = pages.split(",")
        self.auto_update = auto_update
        self.auto_update_plugins = auto_update_plugins
        self.theme = theme
        self.github = github
        self.version = version
        self.version_name = version_name
        self.installed = installed
        self.updated = updated

    def update_check(self):
        with current_app.app_context():
            if current_app.config["EXPECTED_HOME"] not in os.path.realpath(__file__):
                print(
                    f"Not running Installed version in {current_app.config['EXPECTED_HOME']}, therefore not checking for updates"
                )
                return

        connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
        connection.row_factory = sqlite3.Row
        cur = connection.cursor()

        cur.execute("SELECT * FROM ODDASH")
        config = cur.fetchone()

        config = dict(zip(config.keys(), config))
        release = self.get_release(config["github"])

        if not release:
            print("No Releases")
            return

        with TemporaryDirectory() as temp_dir:
            try:
                response = requests.get(release["tarball_url"], stream=True)
                with tarfile.open(fileobj=response.raw, mode=f"r|gz") as tar:
                    tar.extractall(path=temp_dir)
                subprocess.run(
                    [
                        "cp",
                        "-r",
                        "-f",
                        os.path.join(temp_dir, os.listdir(temp_dir)[0], "open_desk_dash"),
                        current_app.config["EXPECTED_HOME"],
                    ]
                )

            except Exception as e:
                print(f"Failed to download latest release\n{e}")

        restart_oddash()

    def get_release(self, link: str) -> dict:
        accountName = link.split("/")[-2]
        repoName = link.split("/")[-1]
        git_api_link = GIT_RELEASE_PATH.format(author=accountName, repo=repoName)

        try:
            response = requests.get(git_api_link)
        except requests.exceptions.ConnectionError:
            print("No internet")
            return {}

        if response.status_code == 403:
            return response.json()
        elif response.status_code != 200:
            return {}
        return response.json()

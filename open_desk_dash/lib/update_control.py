import os
import shutil
import sqlite3
import tarfile
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Dict, List, Union

import requests
from flask import current_app
from open_desk_dash.lib.db_control import get_config_db

GIT_RELEASE_PATH = "https://api.github.com/repos/{author}/{repo}/releases/latest"


def update_check():
    with current_app.app_context():
        if current_app.config["EXPECTED_HOME"] not in os.path.realpath(__file__):
            print(
                f"Not running Installed version in {current_app.config['EXPECTED_HOME']}, therefore not checking for updates"
            )
            return

    connection = get_config_db()
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    cur.execute("SELECT * FROM config")
    config = cur.fetchone()

    config = dict(zip(config.keys(), config))

    github_link = config["github"]
    release = version_check(github_link)

    if not release:
        print("No Release")

    with TemporaryDirectory() as temp_dir:
        try:
            response = requests.get(release["tarball_url"], stream=True)
            with tarfile.open(fileobj=response.raw, mode=f"r|gz") as tar:
                tar.extractall(path=temp_dir)
        except Exception as e:
            print(f"Failed to download latest release\n{e}")

    print(github_link)


def version_check(link: str):
    accountName = link.split("/")[-2]
    repoName = link.split("/")[-1]
    git_api_link = GIT_RELEASE_PATH.format(author=accountName, repo=repoName)
    try:
        response = requests.get(git_api_link)
    except requests.exceptions.ConnectionError:
        print("No internet")
        return None
    if response.status_code != 200:
        return None
    return response.json()

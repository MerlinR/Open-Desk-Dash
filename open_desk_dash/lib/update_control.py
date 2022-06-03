import os
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Union

import requests
from open_desk_dash.lib.db_control import get_config_db

GIT_RELEASE_PATH = "https://api.github.com/repos/{author}/{repo}/releases/latest"


def update_check():
    connection = get_config_db()
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    cur.execute("SELECT * FROM config")
    config = cur.fetchone()

    config = dict(zip(config.keys(), config))

    github_link = config["github"]
    release = version_check(github_link)
    if release:
        print(release)
    else:
        print("No Release")
    print(github_link)


def version_check(link: str):
    accountName = link.split("/")[-2]
    repoName = link.split("/")[-1]
    git_api_link = GIT_RELEASE_PATH.format(author=accountName, repo=repoName)
    response = requests.get(git_api_link)
    if response.status_code != 200:
        return None
    return response.json()

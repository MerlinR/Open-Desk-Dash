from dataclasses import dataclass
from datetime import datetime


@dataclass
class BaseConfig:
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

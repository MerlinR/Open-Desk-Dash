import inspect
import os
import sqlite3

from flask import current_app

INIT_SCHEMA = "./configs/init_db.sql"


def config_db() -> sqlite3.Connection:
    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")
    if not os.path.exists(db_path):
        connection = sqlite3.connect(db_path)
        connection.executescript(read_schema())
    return sqlite3.connect(db_path)


def read_schema() -> str:
    sql = ""
    with current_app.open_resource(INIT_SCHEMA) as f:
        sql = f.read().decode("utf8")
    return sql


def create_db(schema: str = ""):
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins["path"] in calframe[1][1]:
            name = plugins["name"]
    if not name:
        print("No DB name to create")
        return

    db_path = os.path.join(
        current_app.config["DATABASE_LOCATION"], f"{name}_storage.db"
    )
    connection = sqlite3.connect(db_path)
    connection.executescript(schema)
    connection.close()


def connect_db() -> sqlite3.Connection:
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins["path"] in calframe[1][1]:
            name = plugins["name"]
    if not name:
        print("No DB name to connect too")
        return

    db_path = os.path.join(
        current_app.config["DATABASE_LOCATION"], f"{name}_storage.db"
    )

    if not os.path.exists(db_path):
        print(f"Database for {name} does not exist")
        return None

    return sqlite3.connect(db_path)


def setup_DB_control():
    current_app.create_db = create_db
    current_app.connect_db = connect_db
    current_app.config["Config_Database"] = config_db()

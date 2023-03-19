import inspect
import json
import os
import sqlite3

from flask import current_app, request

from .oddash import ODDash


def get_config_db() -> sqlite3.Connection:
    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    return connection


def read_schema() -> str:
    sql = ""
    with current_app.open_resource(current_app.config["INIT_SCHEMA"]) as f:
        sql = f.read().decode("utf8")
    return sql


def gather_config():
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    load_app_config(request.blueprint)


def connect_db() -> sqlite3.Connection:
    plugin_name = request.blueprint

    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], f"{plugin_name}_storage.db")

    if not os.path.exists(db_path):
        print(f"Database for {plugin_name} does not exist")
        return None

    return sqlite3.connect(db_path)


def gather_app_configs():
    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    cur = connection.cursor()

    for db_name in cur.execute("SELECT * FROM sqlite_master WHERE type = 'table'"):
        if db_name[1] in ["plugins", "ODDASH"]:
            continue
        load_app_config(db_name[1])

    connection.close()


def create_config(configs: dict):
    """
    The create_config will not overwrite existing data, and therefore can be repeated inside setup.
    """
    calling_func = inspect.getouterframes(inspect.currentframe(), 2)[1][1]

    try:
        plugin_name = [
            plugin.name
            for plugin in current_app.config["plugins"].values()
            if plugin.path in calling_func
        ][0]
    except IndexError:
        print("No DB name to create config for")
        return

    sql = f"CREATE TABLE IF NOT EXISTS {plugin_name} (id INTEGER PRIMARY KEY, configs TEXT);"

    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    cur = connection.cursor()
    cur.execute(sql)

    if configs:
        cur.execute(f"SELECT configs FROM {plugin_name}")
        row = cur.fetchone()
        if not row:
            sql = f"REPLACE INTO {plugin_name}(id, configs) VALUES(1, ?);"
            try:
                cur = connection.cursor()
                cur.execute(sql, [json.dumps(configs)])
                connection.commit()
            except Exception as e:
                print(f"Failed to save config for {plugin_name}")
                print(sql, json.dumps(configs))
                print(e)
                connection.rollback()
    connection.close()

    load_app_config(plugin_name)


def save_config(configs: dict):
    """
    Will save a dict of config's into the plugins config DB, must match the created config schema.
    """
    plugin_name = request.blueprint

    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])

    sql = f"REPLACE INTO {plugin_name}(id, configs) VALUES(1, ?);"

    try:
        cur = connection.cursor()
        cur.execute(sql, [json.dumps(configs)])
        connection.commit()
    except Exception as e:
        print(f"Failed to save config for {plugin_name}")
        print(sql, json.dumps(configs))
        print(e)
        connection.rollback()
    finally:
        connection.close()
    load_app_config(plugin_name)


def load_base_config():
    connection = None
    if not os.path.exists(current_app.config["DATABASE_LOCATION"]):
        os.mkdir(current_app.config["DATABASE_LOCATION"])

    if not os.path.exists(current_app.config["CONFIG_DB_LOCATION"]):
        connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
        connection.executescript(read_schema())
    else:
        connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])

    connection.row_factory = sqlite3.Row
    cur = connection.cursor()

    cur.execute(f"SELECT * FROM ODDASH")
    row = cur.fetchone()
    data = dict(zip(row.keys(), row))
    data.pop("id")
    current_app.config["oddash"] = ODDash(**data)
    connection.close()


def load_app_config(name: str):
    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    cur.execute(f"SELECT configs FROM {name}")

    row = cur.fetchone()
    current_app.config[name] = json.loads(row[0])
    connection.close()


def setup_DB_control():
    load_base_config()
    current_app.create_config = create_config
    current_app.gather_config = gather_config
    current_app.save_config = save_config
    current_app.connect_db = connect_db
    gather_app_configs()

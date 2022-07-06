import inspect
import os
import sqlite3

from flask import current_app, request

INIT_SCHEMA = "./configs/init_db.sql"


def get_config_db() -> sqlite3.Connection:
    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    return connection


def gather_config_db() -> sqlite3.Connection:
    connection = None

    if not os.path.exists(current_app.config["CONFIG_DB_LOCATION"]):
        connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
        connection.executescript(read_schema())
    else:
        connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])

    cur = connection.cursor()

    for db_name in cur.execute("SELECT * FROM sqlite_master WHERE type = 'table'"):
        if db_name[1] in ["plugins"]:
            continue
        load_config(db_name[1])

    connection.close()
    current_app.config["config"]["pages"] = current_app.config["config"]["pages"].split(
        ","
    )


def read_schema() -> str:
    sql = ""
    with current_app.open_resource(INIT_SCHEMA) as f:
        sql = f.read().decode("utf8")
    return sql


def create_db(schema: str = ""):
    calling_func = inspect.getouterframes(inspect.currentframe(), 2)[1][1]

    try:
        plugin_name = [
            plugin.name
            for plugin in current_app.config["plugins"].values()
            if plugin.path in calling_func
        ][0]
    except IndexError:
        print("No DB name to create")
        return

    db_path = os.path.join(
        current_app.config["DATABASE_LOCATION"], f"{plugin_name}_storage.db"
    )

    if os.path.exists(db_path):
        print(f"{plugin_name} DB already exists... skipping")
        return None

    connection = sqlite3.connect(db_path)
    connection.executescript(schema)
    connection.close()


def connect_db() -> sqlite3.Connection:
    plugin_name = request.blueprint

    db_path = os.path.join(
        current_app.config["DATABASE_LOCATION"], f"{plugin_name}_storage.db"
    )

    if not os.path.exists(db_path):
        print(f"Database for {plugin_name} does not exist")
        return None

    return sqlite3.connect(db_path)


def create_config(schema: dict, init_data: dict = None):
    """
    Creates a Database in standard location with the plugin's name, called with a config options and optionally initial data.
    The Config schema converts to SQL types therefore, must be either str,int,float or None(BLOB).
    {
        "title": int,
        "imageLink": str,
    },
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

    sql_schema_list = []
    types = {str: "TEXT", int: "INTEGER", float: "FLOAT", list: "TEXT", None: "BLOB"}
    for key, value in schema.items():
        if value not in [str, int, float, list, None]:
            print(f"Error: {plugin_name} Config {key} attempting to save as {value}")
        else:
            sql_schema_list.append(f"{key} {types[value]}")

    sql = f"CREATE TABLE IF NOT EXISTS {plugin_name} (id INTEGER PRIMARY KEY, {','.join(sql_schema_list)});"

    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    cur = connection.cursor()
    cur.execute(sql)

    cur.execute(f"SELECT * FROM {plugin_name}")
    row = cur.fetchone()
    if init_data and not row:
        values_cleaned = pack_dict_to_list(init_data)

        sql = f"REPLACE INTO {plugin_name}(id,{','.join(init_data.keys())}) VALUES(1,{','.join(values_cleaned)});"

        try:
            cur = connection.cursor()
            cur.execute(sql)

            connection.commit()
        except Exception as e:
            print(f"Failed to save config for {plugin_name}")
            print(sql)
            print(e)
            connection.rollback()

    connection.close()

    load_config(plugin_name)


def gather_config():
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    load_config(request.blueprint)


def save_config(config: dict):
    """
    Will save a dict of config's into the plugins config DB, must match the created config schema.
    """
    plugin_name = request.blueprint

    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    values_cleaned = pack_dict_to_list(config)

    sql = f"REPLACE INTO {plugin_name}(id,{','.join(config.keys())}) VALUES(1,{','.join(values_cleaned)});"

    try:
        cur = connection.cursor()
        cur.execute(sql)

        connection.commit()
    except Exception as e:
        print(f"Failed to save config for {plugin_name}")
        print(sql)
        print(e)
        connection.rollback()
    finally:
        connection.close()
    load_config(plugin_name)


def load_config(name: str):
    connection = sqlite3.connect(current_app.config["CONFIG_DB_LOCATION"])
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM {name}")

    row = cur.fetchone()
    connection.close()
    current_app.config[name] = dict(zip(row.keys(), row))


def pack_dict_to_list(data: dict) -> list:
    """
    Convert all values to a str surrounded by single speech mark so can be saved into SQL,
    convert int/float to str but not surrounding to ensure read as a int/float
    """
    new_data = []
    for val in data.values():
        if isinstance(val, list):
            new_data.append(f"'{','.join(str(val))}'")
        elif isinstance(val, str):
            new_data.append(f"'{val}'")
        else:
            new_data.append(str(val))
    return new_data


def setup_DB_control():
    current_app.create_config = create_config
    current_app.gather_config = gather_config
    current_app.save_config = save_config
    current_app.create_db = create_db
    current_app.connect_db = connect_db
    gather_config_db()

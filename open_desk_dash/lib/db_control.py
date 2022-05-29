import inspect
import os
import sqlite3

from flask import current_app

INIT_SCHEMA = "./configs/init_db.sql"


def get_config_db() -> sqlite3.Connection:
    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")
    connection = sqlite3.connect(db_path)
    return connection


def gather_config_db() -> sqlite3.Connection:
    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")
    connection = None
    if not os.path.exists(db_path):
        connection = sqlite3.connect(db_path)
        connection.executescript(read_schema())
    else:
        connection = sqlite3.connect(db_path)

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
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            name = plugins.name
    if not name:
        print("No DB name to create")
        return

    db_path = os.path.join(
        current_app.config["DATABASE_LOCATION"], f"{name}_storage.db"
    )
    if os.path.exists(db_path):
        print(f"DB for {name} exists")
        return None

    connection = sqlite3.connect(db_path)
    connection.executescript(schema)
    connection.close()


def connect_db() -> sqlite3.Connection:
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            name = plugins.name
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
    calframe = inspect.getouterframes(inspect.currentframe(), 2)

    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            name = plugins.name
    if not name:
        print("No DB name to create")
        return

    sql_schema_list = []
    types = {str: "TEXT", int: "INTEGER", float: "FLOAT", None: "BLOB"}
    for key, value in schema.items():
        if value not in [str, int, float, None]:
            print(f"Error: {name} Config {key} attempting to save as {value}")
        else:
            sql_schema_list.append(f"{key} {types[value]}")

    sql = f"CREATE TABLE IF NOT EXISTS {name} (id INTEGER PRIMARY KEY, {','.join(sql_schema_list)});"

    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")

    connection = sqlite3.connect(db_path)
    connection.executescript(sql)

    cur = connection.cursor()
    cur.execute(f"SELECT * FROM {name}")
    row = cur.fetchone()
    if init_data and not row:
        values_cleaned = pack_dict_to_list(init_data)

        sql = f"REPLACE INTO {name}(id,{','.join(init_data.keys())}) VALUES(1,{','.join(values_cleaned)});"

        try:
            cur = connection.cursor()
            cur.execute(sql)

            connection.commit()
        except Exception as e:
            print(f"Failed to save config for {name}")
            print(sql)
            print(e)
            connection.rollback()

    load_config(name)
    connection.close()


def gather_config():
    """
    Will gather the plugin's Config into the global variables, automatically called when saving configs.
    """
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugins in current_app.config["plugins"].values():
        if plugins.path in calframe[1][1]:
            name = plugins.name
    if not name:
        print("No DB name to create")
        return

    load_config(name)


def save_config(config: dict):
    """
    Will save a dict of config's into the plugins config DB, must match the created config schema.
    """
    calframe = inspect.getouterframes(inspect.currentframe(), 2)
    name = None
    for plugin in current_app.config["plugins"].values():
        if plugin.path in calframe[1][1]:
            name = plugin.name
    if not name:
        print("No DB name to create")
        return

    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")

    connection = sqlite3.connect(db_path)
    values_cleaned = pack_dict_to_list(config)

    sql = f"REPLACE INTO {name}(id,{','.join(config.keys())}) VALUES(1,{','.join(values_cleaned)});"

    try:
        cur = connection.cursor()
        cur.execute(sql)

        connection.commit()
    except Exception as e:
        print(f"Failed to save config for {name}")
        print(sql)
        print(e)
        connection.rollback()
    finally:
        connection.close()
    load_config(name)


def load_config(name: str):
    db_path = os.path.join(current_app.config["DATABASE_LOCATION"], "config_storage.db")

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    cur = connection.cursor()
    cur.execute(f"SELECT * FROM {name}")

    row = cur.fetchone()
    connection.close()
    current_app.config[name] = dict(zip(row.keys(), row))


def pack_dict_to_list(data: dict) -> list:
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

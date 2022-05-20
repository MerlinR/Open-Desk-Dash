import os
import secrets

SECRET_KEY_FILE = "./config/key.txt"


def load_secret_key() -> str:
    key = ""
    if os.path.isfile(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, encoding="utf8") as f:
            for line in f:
                key = line.strip()
    else:
        key = create_secret_key()

    return key


def create_secret_key() -> str:
    key = secrets.token_hex()

    try:
        with open(SECRET_KEY_FILE, "w") as f:
            f.write(key)
    except PermissionError as e:
        print("Failed to generate key due to lack of permissions error.")
        return ""
    print(f"New key generated: {key}")
    return key


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = load_secret_key()
    # FLASK_HTPASSWD_PATH = "/secret/.htpasswd"
    FLASK_SECRET = SECRET_KEY
    # DB_HOST = "database"


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    # DB_HOST = "my.production.database"

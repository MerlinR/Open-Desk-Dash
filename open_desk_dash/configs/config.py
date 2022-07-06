class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = "OpenDeskDash"
    FLASK_SECRET = SECRET_KEY
    DATABASE_LOCATION = "configs/dbs/"
    CONFIG_DB_LOCATION = "configs/dbs/config_storage.db"


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False

class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = "OpenDeskDash"
    FLASK_SECRET = SECRET_KEY
    DATABASE_LOCATION = "dbs/"
    CONFIG_DB_LOCATION = "dbs/config_storage.db"
    EXPECTED_HOME = "/opt/opendeskdash/"


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False

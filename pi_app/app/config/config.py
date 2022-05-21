class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    TEMPLATES_AUTO_RELOAD = True
    SECRET_KEY = "OpenDeskDash"
    FLASK_SECRET = SECRET_KEY
    # DB_HOST = "database"


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    # DB_HOST = "my.production.database"

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEBUG = False

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['TESTING_DATABASE_URL']
    TESTING = True

import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PORT = 5000
    # Customization
    RECOMMENDER_DEFAULT_COUNT = 10
    RECOMMENDER_ALPHA = 3
    RECOMMENDER_BETA = 0.01
    RECOMMENDER_MIN_ITEM_FREQUENCY = 5
    RECOMMENDER_MIN_USER_FREQUENCY = 3

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

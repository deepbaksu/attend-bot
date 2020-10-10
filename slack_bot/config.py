import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@0.0.0.0/postgres"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

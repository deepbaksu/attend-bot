import logging
from typing import Optional

import flask
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

from slack_bot.config import Config, TestConfig

logging.basicConfig(level=logging.INFO)

KST = timezone("Asia/Seoul")
db = SQLAlchemy()


def create_app(environment: Optional[str]) -> flask.Flask:

    app = Flask(__name__)

    if environment == "production":
        app.config.from_object(Config)
    else:
        app.config.from_object(TestConfig)

    db.init_app(app)
    migrate = Migrate(app, db)

    from slack_bot import routes

    app.register_blueprint(routes.api, url_prefix="/")

    return app


supported_channels = {"attend", "test-channel-for-bots"}

with open("slack_bot/saying.txt", encoding="utf-8") as f:
    lines = f.readlines()

from slack_bot import models, routes

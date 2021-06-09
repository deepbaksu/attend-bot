import logging
from typing import Optional

import flask
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

from slack_bot.config import Config, TestConfig
from slack_bot.quote import Quote, load_quotes

logging.basicConfig(level=logging.INFO)

KST = timezone("Asia/Seoul")
db = SQLAlchemy()

supported_channels = {"attend", "test-channel-for-bots"}

quotes = load_quotes()
assert len(quotes) > 1, "There should be more than 1 quote but found only 1 quote"


def create_app(environment: Optional[str]) -> flask.Flask:
    app = Flask(__name__)

    if environment == "production":
        app.config.from_object(Config)
    else:
        app.config.from_object(TestConfig)

    db.init_app(app)
    Migrate(app, db)

    from slack_bot import routes

    app.register_blueprint(routes.api, url_prefix="/")

    return app

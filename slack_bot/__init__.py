import logging

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

from slack_bot.config import Config

logging.basicConfig(level=logging.INFO)

KST = timezone("Asia/Seoul")
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

supported_channels = {"attend"}

with open("slack_bot/saying.txt", encoding="utf-8") as f:
    lines = f.readlines()

from slack_bot import routes, models

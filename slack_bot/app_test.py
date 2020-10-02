import os
import tempfile

import flask
import datetime
import pytz

import pytest
import json

from slack_bot.app import app, get_message


@pytest.fixture
def client():
    db_fd, app.config["DATABASE"] = tempfile.mkstemp()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    os.unlink(app.config["DATABASE"])


def test_attend(client):
    """Start with a blank database."""

    rv = client.post("/attend", data=dict(user_name="kkweon"))

    data = json.loads(rv.data)

    assert data["response_type"] == "in_channel"
    assert "*kkweon님 출석체크*" in data["text"]


def test_get_message():
    username = "kkweon"
    date = datetime.datetime(
        year=2020,
        month=10,
        day=1,
        hour=22,
        minute=56,
        tzinfo=pytz.timezone("Asia/Seoul"),
    )
    quote = "HELLO"

    assert f"""*kkweon님 출석체크*
10월 01일 출근시간은 한국시각기준 22시 56분입니다.

HELLO
""" == get_message(
        date, username, quote
    )

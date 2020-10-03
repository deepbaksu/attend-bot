import datetime
import json
import os
import tempfile

import flask
import pytest
import pytz
import werkzeug.test

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
    """POST /attend should return 출석체크"""

    rv = client.post("/attend", data=dict(user_name="kkweon"))

    data = json.loads(rv.data)

    assert "in_channel" == data["response_type"]
    assert "*kkweon님 출석체크*" in data["text"]


def test_healthcheck(client: werkzeug.test.Client):
    """GET /healthcheck should return ok and 200"""
    rv = client.get("/healthcheck")
    assert 200 == rv.status_code
    assert b"ok" == rv.data


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

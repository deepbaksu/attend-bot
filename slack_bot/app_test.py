import datetime
import json
import os
import tempfile

import flask
import pytest
import pytz
import werkzeug.test

from slack_bot import app, db
from slack_bot.config import TestConfig
from slack_bot.models import Attendance, User
from slack_bot.routes import get_message

ATTEND = "/attend"


@pytest.fixture
def client():
    app.config.from_object(TestConfig)
    app.config["TESTING"] = True

    db.drop_all()
    db.create_all()

    with app.test_client() as client:
        yield client


def test_attend(client):
    beg = datetime.datetime.now()

    rv = client.post(
        ATTEND, data=dict(user_id="1234", user_name="kkweon", channel_name="attend"),
    )

    data = json.loads(rv.data)

    assert "in_channel" == data["response_type"]
    assert "*kkweon님 출석체크*" in data["text"]

    user = User.query.filter(User.id == "1234").first()
    assert user is not None
    assert "1234" == user.id
    assert "kkweon" == user.username

    attendances = Attendance.query.all()
    assert len(attendances) == 1

    a: Attendance = attendances[0]

    assert a.user == user
    assert a.timestamp > beg


def test_attend_with_wrong_channel(client):
    rv = client.post(
        ATTEND, data=dict(user_name="kkweon", channel_name="wrong_channel")
    )

    assert "출석체크는 다음 채널에서만 사용 가능합니다:" in rv.data.decode("utf-8")


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

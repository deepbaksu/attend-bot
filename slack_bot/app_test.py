import datetime
import json
import os
import tempfile

import flask
import pytest
import pytz
import werkzeug.test

from slack_bot import KST, Quote, create_app, db
from slack_bot.config import TestConfig
from slack_bot.models import Attendance, User
from slack_bot.routes import get_message

ROUTES_DATETIME = "slack_bot.routes.datetime"

ATTEND = "/attend"


@pytest.fixture
def client():
    app = create_app("development")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client


def test_attend_midnight(client, mocker):
    day1 = KST.localize(
        datetime.datetime(2020, 1, 1, hour=1, minute=1, second=0, microsecond=0)
    )

    mocked_datetime = mocker.patch(ROUTES_DATETIME)
    mocked_datetime.now.return_value = day1

    response = client.post(
        ATTEND, data=dict(user_id="1234", user_name="kkweon", channel_name="attend")
    )

    assert mocked_datetime.now.has_been_called()
    assert b"1. kkweon 01:01 AM" in response.data

    day2 = day1 + datetime.timedelta(days=1)
    mocked_datetime.now.return_value = day2

    response = client.post(
        ATTEND, data=dict(user_id="1235", user_name="dragon", channel_name="attend")
    )

    assert mocked_datetime.now.has_been_called()
    assert b"1. dragon 01:01 AM" in response.data

    mocked_datetime.now.return_value = day2 + datetime.timedelta(hours=1)

    response = client.post(
        ATTEND, data=dict(user_id="1234", user_name="kkweon", channel_name="attend")
    )

    assert mocked_datetime.now.has_been_called()
    assert b"2. kkweon 02:01 AM" in response.data


def test_attend(client, mocker):
    mocked_datetime = mocker.patch(ROUTES_DATETIME)
    mocked_datetime.now.return_value = datetime.datetime(
        2020, 1, 1, hour=0, minute=0, second=0, tzinfo=KST
    )

    rv = client.post(
        ATTEND,
        data=dict(user_id="1234", user_name="kkweon", channel_name="attend"),
    )

    data = json.loads(rv.data)

    assert "in_channel" == data["response_type"]
    assert "kkweon님 출석체크" in data["blocks"][0]["text"]["text"]

    user = User.query.filter(User.id == "1234").first()
    assert user is not None
    assert "1234" == user.id
    assert "kkweon" == user.username

    attendances = Attendance.query.all()
    assert len(attendances) == 1

    a: Attendance = attendances[0]

    assert a.user == user
    assert a.timestamp == datetime.datetime(
        2020, 1, 1, hour=0, minute=0, second=0, tzinfo=KST
    )


def test_attend_block(client, mocker):
    mocked_datetime = mocker.patch(ROUTES_DATETIME)
    mocked_datetime.now.return_value = KST.localize(
        datetime.datetime(year=2020, month=1, day=2, hour=3, minute=4, second=5)
    )

    mocked_random = mocker.patch("slack_bot.routes.random")
    mocked_random.randint.return_value = 4

    rv = client.post(
        ATTEND,
        data=dict(user_id="1234", user_name="kkweon", channel_name="attend"),
    )

    data = json.loads(rv.data)
    expected = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "kkweon님 출석체크", "emoji": True},
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": "01월 02일 출근시간은 한국시각기준 03시 04분입니다.",
                    "emoji": True,
                },
            },
            {"type": "divider"},
            {"type": "section", "text": {"type": "mrkdwn", "text": "*출석 순위 :rocket:*"}},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "1. kkweon 03:04 AM"},
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "> 자존심은 어리석은 자의 소유물이다.\n> - 헤로도토스"},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "좋아요 :+1:",
                            "emoji": True,
                        },
                        "value": "4",
                        "action_id": "like_quote",
                    }
                ],
            },
        ]
    }

    assert data["blocks"] == expected["blocks"]


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


def test_subscribe(client: werkzeug.test.Client):
    """Tests handling Slack Event Subscription"""
    rv = client.post(
        "/subscribe",
        json={
            "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
            "challenge": "my-challenge",
            "type": "url_verification",
        },
    )

    assert 200 == rv.status_code
    assert "text/plain" in rv.headers["Content-Type"]
    assert b"my-challenge" == rv.data


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

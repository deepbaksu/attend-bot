import json
import random
from datetime import datetime, timedelta
from typing import Iterable, List, Optional

import requests
from flask import current_app, jsonify, make_response, request
from flask.blueprints import Blueprint

from slack_bot import KST, db, quotes, supported_channels
from slack_bot.models import Attendance, QuoteRating, User

NEWLINE = "\n"

api = Blueprint("api", __name__)


def get_attendances_messages(attendances) -> List[str]:
    attendance_list = []
    for idx, att in enumerate(attendances):
        attendance_list.append(
            f"{idx + 1}. {att.user.username} {att.timestamp.astimezone(KST).strftime('%I:%M %p')}"
        )
    return attendance_list


@api.route("/healthcheck", methods=["GET"])
def healthcheck():
    return "ok"


def get_channel_names(channel_names: Iterable[str]) -> str:
    """Returns comma separated names after switching to channel.

    Args:
        channel_names: channel names

    Returns:
        It returns a string that all channel names are concatenated.

    >>> get_channel_names({ "attend", "channel1" })
    "#attend, #channel1"
    """
    return ", ".join(map(lambda name: f"#{name}", channel_names))


def block_handler(
    username: str,
    kr_datetime: datetime,
    quote_id: int,
    attendances: Iterable[Attendance],
):
    datetime_msg = kr_datetime.strftime("%m월 %d일 출근시간은 한국시각기준 %H시 %M분입니다.")

    quote = quotes[quote_id]

    block_template = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"@{username}님 출석체크", "emoji": True},
        },
        {
            "type": "section",
            "text": {"type": "plain_text", "text": datetime_msg, "emoji": True},
        },
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": "*출석 순위 :rocket:*"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "\n".join(get_attendances_messages(attendances)),
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f">{quote.quote}\n>{quote.print_meta()}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "좋아요 :+1:", "emoji": True},
                    "value": f"{quote_id}",
                    "action_id": "like_quote",
                }
            ],
        },
    ]

    return jsonify(blocks=block_template, response_type="in_channel")


@api.route("/attend", methods=["POST"])
def attend():
    current_app.logger.info("Received request.form = %s", request.form)
    current_app.logger.info("Headers\n%s", request.headers)

    channel_name = request.form.get("channel_name")

    current_app.logger.info(channel_name)

    if channel_name not in supported_channels:
        return f"출석체크는 다음 채널에서만 사용 가능합니다: {get_channel_names(supported_channels)}"

    kr_time: datetime = datetime.now().astimezone(KST)

    user_id = request.form.get("user_id")
    user_name = request.form.get("user_name")

    u: Optional[User] = User.query.filter(User.id == user_id).first()

    if u is None:
        u = User(id=user_id, username=user_name)
        db.session.add(u)
        db.session.commit()

    a = Attendance(timestamp=kr_time, user_id=user_id)
    db.session.add(a)
    db.session.commit()

    base_time = kr_time.replace(hour=0, minute=0, second=0, microsecond=0)

    attendances = Attendance.get_earliest_n(5, base_time)

    return block_handler(
        username=user_name,
        kr_datetime=kr_time,
        quote_id=random.randint(0, len(quotes)),
        attendances=attendances,
    )


@api.route("/subscribe", methods=["POST"])
def subscribe():
    """Handles Slack Event Subscriptions"""

    # Event subscription challenge uses JSON
    data = request.get_json()

    if data is None:
        # Block Kit interaction uses Form data. WTF Slack?
        data = json.loads(request.form["payload"])

    current_app.logger.info("/subscribe is called. data = %s", data)

    if data and data.get("type", None) == "url_verification":
        resp = make_response(data.get("challenge"), 200)
        resp.mimetype = "text/plain"
        return resp

    if data and data.get("type", None) == "block_actions":

        user = data["user"]

        username = user["username"]
        user_id = user["id"]

        user = User.query.get(user_id)

        if user is None:
            user = User(id=user_id, username=username)
            db.session.add(user)
            db.session.commit()

        response_url = data["response_url"]

        actions = data.get("actions", [])

        for action in actions:
            if action["action_id"] == "like_quote":
                quote_id = int(action["value"])
                action_ts, action_us = map(int, action["action_ts"].split("."))
                ts = datetime.utcfromtimestamp(action_ts) + timedelta(
                    microseconds=action_us
                )

                LIKE = 1
                quote = QuoteRating(
                    quote_id=quote_id, user_id=user_id, rate=LIKE, timestamp=ts
                )
                db.session.add(quote)
                db.session.commit()

                requests.post(
                    response_url,
                    json=dict(text=f"{username}님 피드백 감사합니다!", replace_original=False),
                )

        return "ok"

    return "ok"

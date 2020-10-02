import datetime
import random
import logging

from flask import Flask, jsonify, request
from pytz import timezone, utc

logging.basicConfig(level=logging.INFO)

KST = timezone("Asia/Seoul")
app = Flask(__name__)

with open("slack_bot/saying.txt", encoding="utf-8") as f:
    lines = f.readlines()


def get_message(date: datetime, username: str, quote: str) -> str:
    """Returns Slack formatted message

    Args:
        date: Datetime object where 출첵 is done.
        username: Username
        quote: 맨 마지막에 추가할 인용 문구

    Returns:
        A message sent to the user
    """
    # 윈도우에서는 strftime을 이용하여 날짜형태를 변경하고 한글을 결합할 경우
    # UnicodeEncodeError 및 Invalid format string 오류가 발생할 수 있습니다.
    # Korean + time.strftime() 문제해결을 위해 다음의 링크를 참고하였습니다.
    # https://hcid-courses.github.io/TA/QnA/issues_with_windows_korean_strftime.html
    datetime_msg = (
        date.strftime(
            "%m월 %d일 출근시간은 한국시각기준 %H시 %M분입니다.".encode("unicode-escape").decode()
        )
        .encode()
        .decode("unicode-escape")
    )
    return f"""*{username}님 출석체크*
{datetime_msg}

{quote}
"""


@app.route("/attend", methods=["GET", "POST"])
def attend():

    logging.info("Received request.form = %s", request.form)

    now = datetime.datetime.utcnow()
    kr_time = utc.localize(now).astimezone(KST)

    msg = {
        "response_type": "in_channel",
        "text": get_message(kr_time, request.form["user_name"], random.choice(lines)),
    }

    logging.info("Sending a response back %s", msg)

    return jsonify(msg)


if __name__ == "__main__":
    app.run(debug=True)

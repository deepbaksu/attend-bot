import datetime
import random

from flask import Flask, jsonify, request
from pytz import timezone, utc

KST = timezone("Asia/Seoul")
app = Flask(__name__)

with open("slack_bots/saying.txt", encoding="utf-8") as f:
    lines = f.readlines()

@app.route("/attend", methods=["GET", "POST"])
def attend():
    now = datetime.datetime.utcnow()
    kr_time = utc.localize(now).astimezone(KST)

    # 윈도우에서는 strftime을 이용하여 날짜형태를 변경하고 한글을 결합할 경우
    # UnicodeEncodeError 및 Invalid format string 오류가 발생할 수 있습니다.
    # Korean + time.strftime() 문제해결을 위해 다음의 링크를 참고하였습니다.
    # https://hcid-courses.github.io/TA/QnA/issues_with_windows_korean_strftime.html
    datetime_msg = (
        kr_time.strftime(
            "%m월 %d일 출근시간은 한국시각기준 %H시 %M분입니다.".encode("unicode-escape").decode()
        )
        .encode()
        .decode("unicode-escape")
    )

    username = request.form["user_name"]

    text = f"""*{username}님 출석체크*
{datetime_msg}

{random.choice(lines)}
"""

    msg = {
        "response_type": "in_channel",
        "text": text,
    }

    return jsonify(msg)


if __name__ == "__main__":
    app.run(debug=True)

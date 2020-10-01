from flask import Flask, jsonify
from flask import request
import datetime
from pytz import timezone, utc

KST = timezone('Asia/Seoul')
app = Flask(__name__)

@app.route('/attend', methods=['GET', 'POST'])
def attend():
    now = datetime.datetime.utcnow()
    kr_time = utc.localize(now).astimezone(KST)

    # 윈도우에서는 strftime을 이용하여 날짜형태를 변경하고 한글을 결합할 경우 
    # UnicodeEncodeError 및 Invalid format string 오류가 발생할 수 있습니다.
    # Korean + time.strftime() 문제해결을 위해 다음의 링크를 참고하였습니다.
    # https://hcid-courses.github.io/TA/QnA/issues_with_windows_korean_strftime.html
    msg = {
            "response_type": "in_channel",
            "text":'*'+request.form['user_name'] + '님 출석체크* \n' + \
            kr_time.strftime('%m월 %d일 출근시간은 한국시각기준 %H시 %M분입니다.\n'.encode('unicode-escape').decode()).encode().decode('unicode-escape') + \
            '존버는 승리합니다\n\n'} 

    return jsonify(msg)

if __name__ == "__main__":
    app.run(debug=True)

import requests
from flask import Flask
from flask import request, Response
import datetime
from pytz import timezone, utc

KST = timezone('Asia/Seoul')
now = datetime.datetime.utcnow()
kr_time = utc.localize(now).astimezone(KST)


def send_slack(msg):
    res = requests.post('https://hooks.slack.com/services/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', json={
        'text' : msg
    }, headers={'Content-Type': 'application/json'})

app = Flask(__name__)

@app.route('/attend', methods=['GET', 'POST'])
def attend():
    msg = \
        '*'+request.form['user_name'] + '님 출석체크* \n' + str(kr_time).split('.')[0].split(' ')[0].split('-')[1] + '월 '+ \
        str(kr_time).split('.')[0].split(' ')[0].split('-')[2] + '일 '+ \
        '출근시간은 한국시각기준 ' + \
        str(kr_time).split('.')[0].split(' ')[1].split(':')[0] + '시 ' + \
        str(kr_time).split('.')[0].split(' ')[1].split(':')[1] + '분입니다.\n' + '존버는 승리합니다.\n\n'

    send_slack(msg)

    resp = Response(response=None, status=200, mimetype="application/json")
    return resp

if __name__ == "__main__":
    app.run(debug=True)
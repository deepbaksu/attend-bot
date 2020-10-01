import requests
from flask import Flask, jsonify
from flask import request, Response
import datetime
from pytz import timezone, utc
from slack import WebClient
from slack.errors import SlackApiError

client = WebClient(token='xoxb-288745980535-1375995619957-foQqQXR7IUNBwofXwce9Z9Fr')
KST = timezone('Asia/Seoul')
now = datetime.datetime.utcnow()
kr_time = utc.localize(now).astimezone(KST)

app = Flask(__name__)

@app.route('/attend', methods=['GET', 'POST'])
def attend():
    msg = {
        'response_type' : 'in_channel',
        'text' : '*'+request.form['user_name'] + '님 출석체크* \n' + str(kr_time).split('.')[0].split(' ')[0].split('-')[1] + '월 '+ \
        str(kr_time).split('.')[0].split(' ')[0].split('-')[2] + '일 '+ \
        '출근시간은 한국시각기준 ' + \
        str(kr_time).split('.')[0].split(' ')[1].split(':')[0] + '시 ' + \
        str(kr_time).split('.')[0].split(' ')[1].split(':')[1] + '분입니다.\n' + '존버는 승리합니다.\n\n'
    }
    return jsonify(msg)

if __name__ == "__main__":
    app.run(debug=True)

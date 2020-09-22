import json
from flask import Flask, request, make_response
from slacker import Slacker

token = os.environ.get('SLACK_URL')

slack = Slacker(token)
app = Flask(__name__)


@app.route('/slack', methods=['GET', 'POST'])
def hears():
    slack_event = json.loads(request.data)


    print('This is slack event \n', json.dumps(slack_event, indent='\t'))
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200,
                            {"content_type":"application/json"})
    
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return event_handler(event_type, slack_event)
    return make_response("슬랙 요청에 이벤트가 없습니다.", 404,
                            {"X-Slack-No-Retry": 1})

def event_handler(event_type, slack_event):
    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = get_answer()
        print(text)
        slack.chat.post_message(channel, text)
        return make_response("앱 멘션 메시지가 발송되었습니다", 200, {"content_type":"application/json"})

    message = "[%s] 이벤트 핸들러를 찾을 수 없습니다." % event_type
    return make_response(message, 200, {"X-Slack-No-Retry" : 1})

def get_answer():
    return "안녕하세요"

@app.route('/', methods=['GET', 'POST'])
def index():
    return "Hello World!"

if __name__=='__main__':
    app.run('0.0.0.0', port=8080)

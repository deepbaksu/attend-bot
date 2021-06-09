import json

import flask.testing
import pytest
import pytest_mock
import requests

from slack_bot import create_app, db


@pytest.fixture
def client():
    app = create_app("development")
    app.config["TESTING"] = True

    with app.app_context():
        db.drop_all()
        db.create_all()

    with app.test_client() as client:
        yield client
        db.drop_all()


def test_handle_block_actions(
    client: flask.testing.FlaskClient, mocker: pytest_mock.MockerFixture
):
    mocked_request = mocker.patch.object(requests, "post", autospec=True)
    mocked_request.return_value = True

    response_url = "https://www.postresponsestome.com/T123567/1509734234"
    data = {
        "type": "block_actions",
        "user": {
            "id": "<user_id>",
            "username": "kkweon",
            "name": "kkweon",
            "team_id": "<team_id>",
        },
        "api_app_id": "A02",
        "token": "<token>",
        "container": {
            "type": "message",
            "text": "The contents of the original message where the action originated",
        },
        "trigger_id": "12466734323.1395872398",
        "team": {"id": "<team_id>", "domain": "<team_domain>"},
        "enterprise": None,
        "is_enterprise_install": False,
        "state": {"values": {}},
        "response_url": response_url,
        "actions": [
            {
                "type": "button",
                "block_id": "ndZz",
                "action_id": "like_quote",
                "text": {"type": "plain_text", "text": "좋아요 :+1:", "emoji": True},
                "value": "0",
                "action_ts": "1623205619.614215",
            }
        ],
    }

    resp = client.post("/subscribe", data=dict(payload=json.dumps(data)))
    resp.close()
    assert b"ok" == resp.data
    mocked_request.assert_called_once_with(
        response_url, json={"text": "kkweon님 피드백 감사합니다!", "replace_original": False}
    )

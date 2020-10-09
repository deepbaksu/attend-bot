from datetime import datetime, timedelta

import pytest
from flask_sqlalchemy import SQLAlchemy

from slack_bot.models import Attendance, User


@pytest.fixture
def test_db():
    from slack_bot import db

    return db


def test_n(test_db: SQLAlchemy):
    dt = datetime.now()

    user1 = User(id="user1", username="username1")
    user2 = User(id="user2", username="username2")

    test_db.session.add_all([user1, user2])

    a1 = Attendance(timestamp=dt + timedelta(seconds=1), user_id=user1.id)
    a1_2 = Attendance(timestamp=dt, user_id=user1.id)
    a2 = Attendance(timestamp=dt + timedelta(seconds=2), user_id=user2.id)

    test_db.session.add_all([a1, a1_2, a2])
    test_db.session.commit()

    ret = Attendance.get_earliest_n(1, dt.date())
    assert list(ret) == [a1_2]

    ret = Attendance.get_earliest_n(2, dt.date())
    assert list(ret) == [a1_2, a2]

    ret = Attendance.get_earliest_n(2, dt.date() + timedelta(days=1))
    assert list(ret) == []

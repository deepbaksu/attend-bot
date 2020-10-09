from __future__ import annotations
from typing import List, Iterable, Tuple

from sqlalchemy import cast, Date, func
from sqlalchemy.orm import load_only

from slack_bot import db
import datetime
import pytz
from sqlalchemy.types import TypeDecorator


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)

    def __repr__(self):
        return "User(id=%r, username=%r)" % (self.id, self.username)


class UnixEpoch(TypeDecorator):
    impl = db.Integer

    def __init__(self):
        TypeDecorator.__init__(self)

    def process_bind_param(self, value: datetime.datetime, dialect):
        return value.astimezone(tz=pytz.utc).timestamp() * 1000

    def process_result_value(self, value, dialect):
        return datetime.datetime.utcfromtimestamp(value / 1000)


class Attendance(db.Model):
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(UnixEpoch, index=True, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User")

    def __repr__(self):
        return "Attendance(id=%r, datetime=%r, user_id=%r)" % (
            self.id,
            self.timestamp,
            self.user_id,
        )

    @staticmethod
    def get_earliest_n(n: int, target_date: datetime.datetime) -> Iterable[Attendance]:
        another_subquery = (
            Attendance.query.with_entities(Attendance.user_id, Attendance.timestamp)
            .filter(target_date <= Attendance.timestamp)
            .filter(Attendance.timestamp < (target_date + datetime.timedelta(days=1)))
            .subquery()
        )

        subquery = (
            db.session.query(
                another_subquery.c.user_id,
                func.min(another_subquery.c.timestamp).label("min_timestamp"),
            )
            .group_by(another_subquery.c.user_id)
            .order_by("min_timestamp")
            .limit(n)
            .subquery()
        )

        return Attendance.query.filter(Attendance.user_id == subquery.c.user_id).filter(
            Attendance.timestamp == subquery.c.min_timestamp
        )

from __future__ import annotations

import datetime
from typing import Iterable, List, Tuple

import pytz
from sqlalchemy import Date, cast, func
from sqlalchemy.orm import load_only
from sqlalchemy.types import TypeDecorator

from slack_bot import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)

    def __repr__(self):
        return "User(id=%r, username=%r)" % (self.id, self.username)


class Attendance(db.Model):
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.TIMESTAMP(timezone=True), index=True, nullable=False)
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

        subquery = (
            Attendance.query.with_entities(
                Attendance.user_id,
                func.min(Attendance.timestamp).label("min_timestamp"),
            )
            .filter(target_date <= Attendance.timestamp)
            .filter(Attendance.timestamp < (target_date + datetime.timedelta(days=1)))
            .group_by(Attendance.user_id)
            .order_by("min_timestamp")
            .limit(n)
            .subquery()
        )

        return Attendance.query.filter(Attendance.user_id == subquery.c.user_id).filter(
            Attendance.timestamp == subquery.c.min_timestamp
        )

from __future__ import annotations
from typing import List, Iterable

from sqlalchemy import cast, Date, func
from sqlalchemy.orm import load_only

from slack_bot import db
import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)

    def __repr__(self):
        return "User(id=%r, username=%r)" % (self.id, self.username)


class Attendance(db.Model):
    __tablename__ = "attendances"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, index=True, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User")

    def __repr__(self):
        return "Attendance(id=%r, datetime=%r, user_id=%r)" % (
            self.id,
            self.timestamp,
            self.user_id,
        )

    @staticmethod
    def get_earliest_n(n: int, target_date: datetime.date) -> Iterable[Attendance]:
        return (
            Attendance.query.options(load_only(Attendance.user_id, Attendance.timestamp)).filter(
                target_date <= Attendance.timestamp)
                .filter(Attendance.timestamp < target_date + datetime.timedelta(days=1))
                .order_by(Attendance.timestamp)
                .group_by(Attendance.user_id)
                .limit(n)

        )

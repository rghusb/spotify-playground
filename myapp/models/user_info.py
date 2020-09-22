""""""
import datetime

from myapp import db


class UserInfo(db.Model):
    """"""

    __tablename__ = "user_info"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Question Type
    question_type = db.Column("QuestionType", db.String(64))

    # Question Answer
    answer = db.Column("Answer", db.String(128))

    # Date of answer submission
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


def add_user_info(user_id: str, question_type: str = "", answer: str = "",) -> UserInfo:
    """"""
    return UserInfo(user_id=user_id, question_type=question_type, answer=answer,)

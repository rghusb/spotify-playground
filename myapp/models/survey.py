""""""
import datetime

from myapp import db


class Survey(db.Model):
    """"""

    __tablename__ = "surveys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"))

    # Artist name
    question_artist_name = db.Column("QuestionArtistName", db.String(64))
    # Top Tracks vs Top Artists and Same vs Like
    question_type = db.Column("QuestionType", db.String(64))
    # Survey question answer
    answer = db.Column("Answer", db.String(64))

    time_frame = db.Column("TimeFrame", db.String(64))  # Short, Medium, Long term

    # Date of answer submission
    date_created = db.Column("DateCreated", db.DateTime, default=datetime.datetime.utcnow)


def add_survey(
    user_id: str,
    question_artist_name: str = "",
    question_type: str = "",
    answer: str = "",
    time_frame: str = "",
) -> Survey:
    """"""
    return Survey(
        user_id=user_id,
        question_artist_name=question_artist_name,
        question_type=question_type,
        answer=answer,
        time_frame=time_frame,
    )

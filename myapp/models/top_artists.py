""""""
from typing import Optional

from myapp import db
from myapp.models.artists import Artists
from myapp.models.users import Users


top_artists_artists_association = db.Table(
    "top_artists_artists",
    db.metadata,
    db.Column("top_artists_id", db.Integer, db.ForeignKey("top_artists.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)


class TopArtists(db.Model):
    """"""

    __tablename__ = "top_artists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    artists = db.relationship(Artists, secondary=top_artists_artists_association)
    term_length = db.Column("TermLength", db.String(64))


def add_top_artists(user: Users) -> TopArtists:
    """"""
    if query_top_artists(user.get_user_id()) is not None:
        raise RuntimeError(
            f"Top Artists table already exists for user: {user.get_username()}"
        )

    return TopArtists(users=user)


def query_top_artists(user_id: str) -> Optional[TopArtists]:
    query = db.session.query(TopArtists).filter_by(user_id=user_id)
    return query.first()

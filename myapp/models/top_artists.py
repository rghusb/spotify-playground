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
    time_range = db.Column("TimeRange", db.String(64))

    artists = db.relationship(Artists, secondary=top_artists_artists_association)


def add_top_artists(user: Users, time_range: str) -> TopArtists:
    """"""
    if query_top_artists(user.get_user_id(), time_range) is not None:
        raise RuntimeError(
            f"Top Artists table already exists for user: {user.get_username()}"
        )

    return TopArtists(users=user, time_range=time_range)


def query_top_artists(user_id: str, time_range: str) -> Optional[TopArtists]:
    query = db.session.query(TopArtists).filter_by(
        user_id=user_id, time_range=time_range
    )
    return query.first()

""""""
from typing import Optional

from app import db
from app.models.artists import Artists

# from app.models.tracks import Tracks
from app.models.users import Users


top_tracks_artists_association = db.Table(
    "top_tracks_artists",
    db.metadata,
    db.Column("top_tracks_id", db.Integer, db.ForeignKey("top_tracks.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)

# top_tracks_tracks_association = db.Table(
#     "top_tracks_tracks",
#     db.metadata,
#     db.Column("top_tracks_id", db.Integer, db.ForeignKey("top_tracks.id")),
#     db.Column("tracks_id", db.Integer, db.ForeignKey("tracks.id")),
# )


class TopTracks(db.Model):
    """"""

    __tablename__ = "top_tracks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    artists = db.relationship(Artists, secondary=top_tracks_artists_association)
    # tracks = db.relationship(Tracks, secondary=top_tracks_tracks_association)


def add_top_tracks(user: Users) -> TopTracks:
    """"""
    if query_top_tracks(user.get_user_id()) is not None:
        raise RuntimeError(
            f"Top Tracks table already exists for user: {user.get_username()}"
        )

    return TopTracks(users=user)


def query_top_tracks(user_id: str) -> Optional[TopTracks]:
    query = db.session.query(TopTracks).filter_by(user_id=user_id)
    return query.first()

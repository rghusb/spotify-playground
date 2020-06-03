""""""
from typing import Optional

from app import db
from app.models.artists import Artists

# from app.models.tracks import Tracks
from app.models.users import Users


saved_tracks_artists_association = db.Table(
    "saved_tracks_artists",
    db.metadata,
    db.Column("saved_tracks_id", db.Integer, db.ForeignKey("saved_tracks.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)

# saved_tracks_tracks_association = db.Table(
#     "saved_tracks_tracks",
#     db.metadata,
#     db.Column("saved_tracks_id", db.Integer, db.ForeignKey("saved_tracks.id")),
#     db.Column("tracks_id", db.Integer, db.ForeignKey("tracks.id")),
# )


class SavedTracks(db.Model):
    """"""

    __tablename__ = "saved_tracks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    artists = db.relationship(Artists, secondary=saved_tracks_artists_association)
    # tracks = db.relationship(Tracks, secondary=saved_tracks_tracks_association)


def add_saved_tracks(user: Users) -> SavedTracks:
    """"""
    if query_saved_tracks(user.get_user_id()) is not None:
        raise RuntimeError(
            f"Saved Tracks table already exists for user: {user.get_username()}"
        )

    return SavedTracks(users=user)


def query_saved_tracks(user_id: str) -> Optional[SavedTracks]:
    query = db.session.query(SavedTracks).filter_by(user_id=user_id)
    return query.first()

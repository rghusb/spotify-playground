""""""
from typing import Optional

from myapp import db

from myapp.models.users import Users


class SavedTracksArtistsAssociation(db.Model):
    """"""

    __tablename__ = "saved_tracks_artists_association"
    saved_tracks_id = db.Column(
        db.Integer, db.ForeignKey("saved_tracks.id"), primary_key=True
    )
    artists_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)
    saved_tracks = db.relationship("SavedTracks")
    artists = db.relationship("Artists")
    count = db.Column(db.Integer, default=1)


def query_saved_tracks_artists_association(
    saved_tracks_id: str, artists_id: str
) -> Optional[db.session.query]:
    query = db.session.query(SavedTracksArtistsAssociation).filter_by(
        saved_tracks_id=saved_tracks_id, artists_id=artists_id
    )
    return query


class SavedTracks(db.Model):
    """"""

    __tablename__ = "saved_tracks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    association = db.relationship("SavedTracksArtistsAssociation")


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

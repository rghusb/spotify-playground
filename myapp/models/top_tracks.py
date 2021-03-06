""""""
from typing import Optional

from myapp import db

from myapp.models.users import Users


class TopTracksArtistsAssociation(db.Model):
    """"""

    __tablename__ = "top_tracks_artists_association"
    top_tracks_id = db.Column(
        db.Integer, db.ForeignKey("top_tracks.id"), primary_key=True
    )
    artists_id = db.Column(db.Integer, db.ForeignKey("artists.id"), primary_key=True)
    top_tracks = db.relationship("TopTracks")
    artists = db.relationship("Artists")
    count = db.Column(db.Integer, default=1)
    rank = db.Column(db.Integer, default=-1)


def query_top_tracks_artists_association(
    top_tracks_id: str, artists_id: str
) -> Optional[db.session.query]:
    query = db.session.query(TopTracksArtistsAssociation).filter_by(
        top_tracks_id=top_tracks_id, artists_id=artists_id
    )
    return query


class TopTracks(db.Model):
    """"""

    __tablename__ = "top_tracks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    time_range = db.Column("TimeRange", db.String(64))

    association = db.relationship("TopTracksArtistsAssociation")


def add_top_tracks(user: Users, time_range: str) -> TopTracks:
    """"""
    if query_top_tracks(user.get_user_id(), time_range) is not None:
        raise RuntimeError(
            f"Top Tracks table already exists for user: {user.get_username()}"
        )

    return TopTracks(users=user, time_range=time_range)


def query_top_tracks(user_id: str, time_range: str) -> Optional[TopTracks]:
    query = db.session.query(TopTracks).filter_by(
        user_id=user_id, time_range=time_range
    )
    return query.first()

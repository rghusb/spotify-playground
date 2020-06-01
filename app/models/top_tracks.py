""""""
from app import db
from app.models.artists import Artists
from app.models.tracks import Tracks


# top_tracks_artists_association = db.Table(
#     "top_tracks_artists",
#     db.metadata,
#     db.Column("top_tracks_id", db.Integer, db.ForeignKey("top_tracks.id")),
#     db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
# )
#
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

    # artists = db.relationship(Artists, secondary=top_tracks_artists_association)
    # tracks = db.relationship(Tracks, secondary=top_tracks_tracks_association)

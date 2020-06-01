""""""
from app import db

# saved_tracks_artists_association = db.Table(
#     "saved_tracks_artists",
#     db.metadata,
#     db.Column("saved_tracks_id", db.Integer, db.ForeignKey("saved_tracks.id")),
#     db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
# )
#
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

    # artists = db.relationship(Artists, secondary=saved_tracks_artists_association)
    # tracks = db.relationship(Tracks, secondary=saved_tracks_tracks_association)

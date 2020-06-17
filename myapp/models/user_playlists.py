""""""
from myapp import db


# user_playlists_artists_association = db.Table(
#     "user_playlists_artists",
#     db.metadata,
#     db.Column("user_playlists_id", db.Integer, db.ForeignKey("user_playlists.id")),
#     db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
# )
#
# user_playlists_tracks_association = db.Table(
#     "user_playlists_tracks",
#     db.metadata,
#     db.Column("user_playlists_id", db.Integer, db.ForeignKey("user_playlists.id")),
#     db.Column("tracks_id", db.Integer, db.ForeignKey("tracks.id")),
# )


# class UserPlaylists(db.Model):
#     """"""
#
#     __tablename__ = "user_playlists"
#
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.relationship("User", back_populates="user_playlists")
#
#     artists = db.relationship("Artists", secondary=user_playlists_artists_association)
#     tracks = db.relationship("Tracks", secondary=user_playlists_tracks_association)

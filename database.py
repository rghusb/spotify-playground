""""""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# import flask_sqlalchemy
# import SQLAlchemy
# import sqlalchemy
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship


app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db = SQLAlchemy(app)


STRING_LENGTH = 50


class Artists(db.Model):
    """"""

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(STRING_LENGTH))


class Tracks(db.Model):
    """"""

    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(STRING_LENGTH))


saved_tracks_artists_association = db.Table(
    "saved_tracks_artists",
    db.metadata,
    db.Column("saved_tracks_id", db.Integer, db.ForeignKey("saved_tracks.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)

saved_tracks_tracks_association = db.Table(
    "saved_tracks_tracks",
    db.metadata,
    db.Column("saved_tracks_id", db.Integer, db.ForeignKey("saved_tracks.id")),
    db.Column("tracks_id", db.Integer, db.ForeignKey("tracks.id")),
)


class SavedTracks(db.Model):
    """"""

    __tablename__ = "saved_tracks"

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.relationship(User, back_populates="saved_tracks")

    artists = db.relationship(Artists, secondary=saved_tracks_artists_association)
    tracks = db.relationship(Tracks, secondary=saved_tracks_tracks_association)


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
    # user_id = db.relationship("User", back_populates="top_artists")

    artists = db.relationship(Artists, secondary=top_artists_artists_association)


top_tracks_artists_association = db.Table(
    "top_tracks_artists",
    db.metadata,
    db.Column("top_tracks_id", db.Integer, db.ForeignKey("top_tracks.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)

top_tracks_tracks_association = db.Table(
    "top_tracks_tracks",
    db.metadata,
    db.Column("top_tracks_id", db.Integer, db.ForeignKey("top_tracks.id")),
    db.Column("tracks_id", db.Integer, db.ForeignKey("tracks.id")),
)


class TopTracks(db.Model):
    """"""

    __tablename__ = "top_tracks"

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.relationship("User", back_populates="top_tracks")

    artists = db.relationship(Artists, secondary=top_tracks_artists_association)
    tracks = db.relationship(Tracks, secondary=top_tracks_tracks_association)


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


followed_artists_artists_association = db.Table(
    "followed_artists_artists",
    db.metadata,
    db.Column("followed_artists_id", db.Integer, db.ForeignKey("followed_artists.id")),
    db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
)


class FollowedArtists(db.Model):
    """"""

    __tablename__ = "followed_artists"

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.relationship("User", back_populates="followed_artists")

    artists = db.relationship(Artists, secondary=followed_artists_artists_association)


class Users(db.Model):
    """"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(STRING_LENGTH))

    saved_tracks_id = db.Column(db.Integer, db.ForeignKey("saved_tracks.id"))
    saved_tracks = db.relationship(SavedTracks, uselist=False, back_populates="users")

    top_artists_id = db.Column(db.Integer, db.ForeignKey("top_artists.id"))
    top_artists = db.relationship(TopArtists, uselist=False, back_populates="users")

    top_tracks_id = db.Column(db.Integer, db.ForeignKey("top_tracks.id"))
    top_tracks = db.relationship(TopTracks, uselist=False, back_populates="users")

    # user_playlists_id = db.Column(db.Integer, db.ForeignKey("UserPlaylists.id"))
    # user_playlists = db.relationship(
    #     "UserPlaylists", uselist=False, back_populates="users"
    # )

    followed_artists_id = db.Column(db.Integer, db.ForeignKey("followed_artists.id"))
    followed_artists = db.relationship(
        FollowedArtists, uselist=False, back_populates="users"
    )

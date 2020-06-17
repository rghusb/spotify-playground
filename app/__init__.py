""""""
# Utils
# from markupsafe import escape

# Main third party libraries
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db = SQLAlchemy(app)

# Local project imports
from app import constants
from app.spotify.main import add_spotify_user_data
from app.spotify.user_data import UserData, DataPull

# Initialize here for db.create_all()
from app.models import (
    artists,
    # tracks,
    users,
    followed_artists,
    saved_tracks,
    top_artists,
    top_tracks,
)


@app.route("/")
def hello_world():
    return "<h1>Spotify Data Collection Project!</h1>"


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":

        add_spotify_user_data(
            top_tracks_flag=True,
            top_artists_flag=True,
            saved_tracks_flag=True,
            followed_artists_flag=True,
        )
        return "User Added"

    return render_template("login.html")


@app.route("/show_user/")
@app.route("/show_user/<string:username>")
def show_user(username=None):
    if not username:
        return "Please add username to url"
    else:
        user = users.query_username(username)
        if not user:
            return f"No user exists given username: '{username}'"
        else:
            user_top_tracks = top_tracks.query_top_tracks(user.id)
            str_top_tracks = []
            for assoc in user_top_tracks.association:
                str_top_tracks.append(
                    {"name": assoc.artists.name, "count": assoc.count}
                )

            user_top_artists = top_artists.query_top_artists(user.id)
            str_top_artists = [artist.name for artist in user_top_artists.artists]

            user_saved_tracks = saved_tracks.query_saved_tracks(user.id)
            str_saved_tracks = []
            for assoc in user_saved_tracks.association:
                str_saved_tracks.append(
                    {"name": assoc.artists.name, "count": assoc.count}
                )

            user_followed_artists = followed_artists.query_followed_artists(user.id)
            str_followed_artists = [
                artist.name for artist in user_followed_artists.artists
            ]

            return render_template(
                "display_user.html",
                username=username,
                top_tracks=str_top_tracks,
                top_artists=str_top_artists,
                saved_tracks=str_saved_tracks,
                followed_artists=str_followed_artists,
            )

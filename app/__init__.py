""""""
# Utils
from markupsafe import escape

# Main third party libraries
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Local project imports
from app import constants
from app.spotify.user_data import UserData, DataPull

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"

db = SQLAlchemy(app)

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


@app.route("/user/<username>")
def show_user_profile(username):
    # show the user profile for that user
    return "User %s" % escape(username)


@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("hello.html", name=name)


@app.route("/add_user/")
@app.route("/add_user/<string:username>")
def add_user(username=None):
    if not username:
        return "Please add username to url"
    else:
        if users.query_username(username):
            return f"User: '{username}' already exists. Please only create new users for now."
        else:
            add_spotify_user_data(
                username,
                top_tracks_flag=True,
                top_artists_flag=True,
                saved_tracks_flag=True,
                followed_artists_flag=True,
            )
            return f"<h1>User: '{username}' added!</h1>"


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
            str_top_tracks = [artist.name for artist in user_top_tracks.artists]

            user_top_artists = top_artists.query_top_artists(user.id)
            str_top_artists = [artist.name for artist in user_top_artists.artists]

            user_saved_tracks = saved_tracks.query_saved_tracks(user.id)
            str_saved_tracks = [artist.name for artist in user_saved_tracks.artists]

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


def add_spotify_user_data(
    spotify_username: str,
    top_tracks_flag=False,
    top_artists_flag=False,
    saved_tracks_flag=False,
    followed_artists_flag=False,
) -> None:
    """"""
    # Add user
    user = users.add_user(spotify_username)

    # Pull user's data
    number_of_tracks = 20
    time = "medium_term"
    spotify_user_data = UserData(spotify_username)

    if top_tracks_flag:
        top_tracks_pull = spotify_user_data.get_current_user_top_tracks(
            limit=number_of_tracks, time_range=time
        )
        if not top_tracks_pull:
            print("No top tracks data to add.")
        add_data_pull(user, top_tracks_pull)

    if top_artists_flag:
        top_artists_pull = spotify_user_data.get_current_user_top_artists(
            number_of_tracks, 0, time
        )
        if not top_artists_pull:
            print("No top artists data to add.")
        add_data_pull(user, top_artists_pull)

    if saved_tracks_flag:
        saved_tracks_pull = spotify_user_data.get_current_user_saved_tracks_data(
            number_of_tracks, 0
        )
        if not saved_tracks_pull:
            print("No saved tracks data to add.")
        add_data_pull(user, saved_tracks_pull)

    if followed_artists_flag:
        followed_artists_pull = spotify_user_data.get_current_user_followed_artists(
            20, None
        )
        if not followed_artists_pull:
            print("No followed artists data to add.")
        add_data_pull(user, followed_artists_pull)

    db.session.add(user)
    db.session.commit()


def add_data_pull(user: users.Users, data_pull: DataPull) -> None:
    """"""
    if data_pull.type == constants.TOP_TRACKS_PULL_TYPE:
        _add_top_tracks(user, data_pull)
    elif data_pull.type == constants.TOP_ARTISTS_PULL_TYPE:
        _add_top_artists(user, data_pull)
    elif data_pull.type == constants.SAVED_TRACKS_PULL_TYPE:
        _add_saved_tracks(user, data_pull)
    elif data_pull.type == constants.FOLLOWED_ARTISTS_PULL_TYPE:
        _add_followed_artists(user, data_pull)
    else:
        raise RuntimeError(
            f"Can't find matching database table for give data pull type: {data_pull.type}"
        )


def _add_top_tracks(user: users.Users, data_pull: DataPull) -> None:
    """"""
    top_tracks_table = top_tracks.add_top_tracks(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        top_tracks_table.artists.append(art_)

    db.session.add(top_tracks_table)


def _add_top_artists(user: users.Users, data_pull: DataPull) -> None:
    """"""
    top_artists_table = top_artists.add_top_artists(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        top_artists_table.artists.append(art_)

    db.session.add(top_artists_table)


def _add_saved_tracks(user: users.Users, data_pull: DataPull) -> None:
    """"""
    saved_tracks_table = saved_tracks.add_saved_tracks(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        saved_tracks_table.artists.append(art_)

    db.session.add(saved_tracks_table)


def _add_followed_artists(user: users.Users, data_pull: DataPull) -> None:
    """"""
    followed_artists_table = followed_artists.add_followed_artists(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        followed_artists_table.artists.append(art_)

    db.session.add(followed_artists_table)


# if __name__ == "__main__":
#     """"""
#     # try:
#     print("Running...")
#     add_spotify_user_data(
#         "rghusbands",
#         top_tracks_flag=True,
#         top_artists_flag=True,
#         saved_tracks_flag=True,
#         followed_artists_flag=True,
#     )
#     # except Exception as err:
#     #     print(f"{err.__class__.__name__}: {err}")
#     #     print("*** Error ***")
#     # else:
#     print("Success!")

""""""
# Utils
# from markupsafe import escape
import requests

# Main third party libraries
from flask import (
    Flask,
    render_template,
    request,
    session,
    make_response,
    session,
    redirect,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.secret_key = "some-secret-key"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://postgres:asdf1234@localhost/testDatabase"

db = SQLAlchemy(app)

# Local project imports
from myapp import constants, exceptions
from myapp.spotify.main import add_spotify_user_data
from myapp.spotify.user_data import (
    get_current_user_spotify_oath,
    get_authorized_spotify,
    get_current_user_top_artists,
)

# Initialize here for db.create_all()
from myapp.models import (
    artists,
    # tracks,
    users,
    followed_artists,
    saved_tracks,
    top_artists,
    top_tracks,
)


@app.route("/")
@app.route("/home")
def index():
    return render_template("home.html")


@app.route("/clear_session")
def clear_session():
    session.clear()
    return "<h1>Session cleared!</h1>"


# @app.route("/authorization_confirm")
# def authorization_confirm():
#     return "<h1>Auth confirmed!</h1>"


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            session["token_info"], authorized = get_token(session)
            session.modified = True

            if not authorized:
                return render_template(
                    "error.html", error="Error - Not Authorized for SpotiPY data pull."
                )

            token = session.get("token_info").get("access_token")
            if not token:
                return render_template(
                    "error.html",
                    error="Error - No auth token available for SpotiPY data pull.",
                )

            user_sp = get_authorized_spotify(auth_token=token)
            username = add_spotify_user_data(
                user_sp,
                top_tracks_flag=True,
                top_artists_flag=True,
                saved_tracks_flag=True,
                followed_artists_flag=True,
            )
            return redirect(url_for("show_user", username=username))

        except exceptions.UserAlreadyExistsError as exc:
            return redirect(url_for("show_user", username=str(exc)))

        except Exception as exc:
            return render_template(
                "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
            )

    return render_template("home.html")


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
            try:
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
            except Exception as exc:
                return f"{exc.__class__.__name__}: {str(exc)}"


# authorization-code-flow Step 1. Have your application request authorization;
# the user logs in and authorizes access
@app.route("/spotify_auth")
def spotify_authorization():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = get_current_user_spotify_oath()
    auth_url = sp_oauth.get_authorize_url()
    # auth_url = get_authorization_url()
    print(auth_url)
    return redirect(auth_url)


# @app.route("/test")
# def test():
#     return redirect("https://www.google.com")


# @app.route("/index")
# def index():
#     return render_template("index.html")


# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/callback")
def callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
    sp_oauth = get_current_user_spotify_oath()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info

    return redirect(url_for("data_pull"))


# authorization-code-flow Step 3.
# Use the access token to access the Spotify Web API;
# Spotify returns requested data
@app.route("/data_pull")
def data_pull():
    session["token_info"], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return "Not Authorized for SpotiPY data pull."
    # data = request.form
    token = session.get("token_info").get("access_token")
    if not token:
        return "No auth token available for SpotiPY data pull."
    user_sp = get_authorized_spotify(auth_token=token)
    username = user_sp.current_user().get("id", "No username found :(")
    top_artists = get_current_user_top_artists(
        user_sp, limit=10, time_range="medium_term"
    )
    if not top_artists:
        return "No Top Artists"

    return render_template(
        "data_pull.html",
        username=username,
        top_artists=[artist.name for artist in top_artists.artists],
    )


# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get("token_info", False)):
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get("token_info").get("expires_at") - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_oauth = get_current_user_spotify_oath()
        token_info = sp_oauth.refresh_access_token(
            session.get("token_info").get("refresh_token")
        )

    token_valid = True
    return token_info, token_valid

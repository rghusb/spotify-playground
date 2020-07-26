""""""
# Utils
import os
import re
from typing import Dict

# from markupsafe import escape
import requests

# Main third party libraries
from flask import (
    Flask,
    render_template,
    request,
    session,
    make_response,
    redirect,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.secret_key = "some-secret-key"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLite config
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
SQLITE_DATABASE_LOCATION = os.path.join(THIS_FOLDER, "..", "db.sqlite3")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{SQLITE_DATABASE_LOCATION}"

# PostgreSQL config
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = "postgresql://postgres:asdf1234@localhost/testDatabase"

# MySQL config
# app.config[
#     "SQLALCHEMY_DATABASE_URI"
# ] = f"mysql+pymysql://rghusb:asdf1234@rghusb.mysql.pythonanywhere-services.com/rghusb$spotifyDatabase"

db = SQLAlchemy(app)

# Local project imports
from myapp import constants, exceptions
from myapp.spotify.main import add_spotify_user_data
from myapp.spotify.user_data import (
    get_current_user_spotify_oath,
    get_authorized_spotify,
    get_current_user_username,
)

# Initialize here for db.create_all()
from myapp.models import (
    artists,
    users,
    top_artists,
    top_tracks,
    survey,
)


@app.route("/")
@app.route("/home")
def index():
    return render_template("home.html")


@app.route("/redirect_home/", methods=["POST", "GET"])
def redirect_home():
    return redirect(url_for("index"))


@app.route("/clear_session")
def clear_session():
    session.clear()
    return "<h1>Session cleared!</h1>"


@app.route("/thank_you/")
def thank_you():
    return "<h1>Thank you for taking the tastes survey!</h1>"


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        try:
            session["token_info"], authorized = _get_token(session)
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

            spotify_username = get_current_user_username(user_sp)
            if not spotify_username:
                raise RuntimeError("Unable to access current user's username.")

            # Add user
            user = users.add_user(spotify_username)
            db.session.add(user)

            add_spotify_user_data(
                user_sp,
                user,
                top_tracks_flag=True,
                top_artists_flag=True,
                time_range="medium_term",
            )
            db.session.commit()

            return redirect(url_for("show_user", username=spotify_username))

        except exceptions.UserAlreadyExistsError as exc:
            return redirect(url_for("show_user", username=str(exc)))

        except Exception as exc:
            return render_template(
                "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
            )

    elif request.method == "POST":
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens
        #  if you reuse a SpotifyOAuth object.
        sp_oauth = get_current_user_spotify_oath()
        auth_url = sp_oauth.get_authorize_url()
        print(auth_url)
        return redirect(auth_url)

    return redirect(url_for("index"))


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
                user_top_tracks = top_tracks.query_top_tracks(user.id, "medium_term")
                str_top_tracks = []
                for assoc in user_top_tracks.association:
                    str_top_tracks.append(
                        {"name": assoc.artists.name, "count": assoc.count}
                    )

                user_top_artists = top_artists.query_top_artists(user.id, "medium_term")
                str_top_artists = [artist.name for artist in user_top_artists.artists]

                return render_template(
                    "display_user.html",
                    username=username,
                    top_tracks=str_top_tracks,
                    top_artists=str_top_artists,
                )
            except Exception as exc:
                return f"{exc.__class__.__name__}: {str(exc)}"


@app.route("/user_survey/")
@app.route("/user_survey/<string:username>")
def user_survey(username=None):
    if not username:
        return "Please add username to url"
    else:
        user = users.query_username(username)
        if not user:
            return f"No user exists given username: '{username}'"
        else:
            try:
                user_top_tracks = top_tracks.query_top_tracks(user.id, "medium_term")
                top_tracks_lis = []
                for assoc in user_top_tracks.association:
                    top_tracks_lis.append(
                        {"name": assoc.artists.name, "count": assoc.count}
                    )
                sorted_top_tracks = sorted(
                    top_tracks_lis, key=lambda i: i["count"], reverse=True
                )
                sorted_str_top_tracks = [artist["name"] for artist in sorted_top_tracks]

                user_top_artists = top_artists.query_top_artists(user.id, "medium_term")
                str_top_artists = [artist.name for artist in user_top_artists.artists]

                return render_template(
                    "survey_question.html",
                    username=username,
                    top_artists_questions=str_top_artists[:1],
                    top_tracks_questions=sorted_str_top_tracks[:1],
                )
            except Exception as exc:
                return f"{exc.__class__.__name__}: {str(exc)}"


@app.route("/save_survey/<string:username>", methods=["POST", "GET"])
def save_survey(username: str):
    if request.method == "POST":
        print(f"Saving survey for {username}...")
        _save_survey_form(request.form, username)
        return redirect(url_for("thank_you"))
    else:
        return "<h1>Can't save survey as GET request</h1>"


def _save_survey_form(form: dict, username: str) -> None:
    """"""

    def _get_artist(txt: str) -> str:
        lst = txt.split("-")
        return lst[0]

    def _get_bool(txt):
        if re.findall("-yes$", txt):
            return "yes"
        elif re.findall("-no$", txt):
            return "no"
        else:
            raise RuntimeError("Error with survey form tags.")

    if not isinstance(form, dict):
        print("Error - form isn't a dictionary.")
        return None

    for key, value in request.form.items():
        response_type = None
        artist = None
        response = None
        if re.search("top-artist", key):
            response_type = "top-artist"
            artist = _get_artist(key)
            response = _get_bool(key)
        elif re.search("top-artist-local", key):
            response_type = "top-artist-local"
            artist = _get_artist(key)
            response = _get_bool(key)
        elif re.search("top-track", key):
            response_type = "top-track"
            artist = _get_artist(key)
            response = _get_bool(key)
        elif re.search("top-track-local", key):
            response_type = "top-track-local"
            artist = _get_artist(key)
            response = _get_bool(key)
        else:
            raise RuntimeError("Error with survey form tags.")

        current_user = users.query_username(username)
        print(
            f"User: {current_user} - Artist: {artist} - Response: {response} - Response Type: {response_type}"
        )

        if current_user and artist and response_type and response:
            new_survey = survey.add_survey(
                current_user.get_user_id(),
                artist,
                response_type,
                response,
                "medium-term",
            )
            db.session.add(new_survey)

    db.session.commit()


# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/callback")
def callback():
    # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens
    #  if you reuse a SpotifyOAuth object.
    sp_oauth = get_current_user_spotify_oath()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code, check_cache=False)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info

    return redirect(url_for("login"))


# Checks to see if token is valid and gets a new token if not
def _get_token(sesh):
    token_valid = False
    token_info = sesh.get("token_info", {})

    # Checking if the session already has a token stored
    if not (sesh.get("token_info", False)):
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = sesh.get("token_info").get("expires_at") - now < 60

    # Refreshing token if it has expired
    if is_token_expired:
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens
        #  if you reuse a SpotifyOAuth object
        sp_oauth = get_current_user_spotify_oath()
        token_info = sp_oauth.refresh_access_token(
            sesh.get("token_info").get("refresh_token")
        )

    token_valid = True
    return token_info, token_valid

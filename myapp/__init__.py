""""""
# Utils
import os
import re
import logging
from typing import Dict, Tuple, List

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

FORMAT = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(
    filename="myapp.log",
    format="%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)

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

app.config["SQLALCHEMY_POOL_RECYCLE"] = 90
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

db = SQLAlchemy(app)

# Local project imports
from myapp import constants, exceptions, utils
from myapp.spotify.main import (
    add_spotify_user_data,
    query_sorted_top_artists,
    query_sorted_top_tracks,
)
from myapp.spotify.user_data import (
    get_current_user_spotify_oath,
    get_authorized_spotify,
    get_current_user,
)

# Initialize here for db.create_all()
from myapp.models import (
    artists,
    users,
    top_artists,
    top_tracks,
    survey,
    user_info,
)


@app.route("/")
@app.route("/home")
def index():
    logger.info("INDEX")
    return render_template("home.html")


@app.route("/redirect_home/", methods=["POST", "GET"])
def redirect_home():
    logger.info("REDIRECT HOME")
    return redirect(url_for("index"))


@app.route("/clear_session")
def clear_session():
    logger.info("SESSION CLEAR")
    session.clear()
    return "<h1>Session cleared!</h1>"


@app.route("/thank_you/")
def thank_you():
    logger.info("THANK YOU")
    return render_template(
        "error.html", error="Thank you for taking the tastes survey!"
    )


@app.route("/login/", methods=["POST", "GET"])
def login():
    logger.info("LOGIN")
    if request.method == "GET":
        try:
            session["token_info"], authorized = _get_token(session)
            session.modified = True

            if not authorized:
                logger.error("Error - Not Authorized for SpotiPY data pull.")
                return render_template(
                    "error.html", error="Error - Not Authorized for SpotiPY data pull."
                )

            token = session.get("token_info").get("access_token")
            if not token:
                logger.error("Error - No auth token available for SpotiPY data pull.")
                return render_template(
                    "error.html",
                    error="Error - No auth token available for SpotiPY data pull.",
                )

            user_sp = get_authorized_spotify(auth_token=token)

            current_user = get_current_user(user_sp)
            if not current_user.username:
                logger.error(f"Couldn't get current user Spotify username")
                return render_template(
                    "error.html", error=f"Unable to access current user's username."
                )

            # Add user
            user = users.add_user(
                current_user.username, current_user.display_name, current_user.email
            )
            db.session.add(user)

            for time_range in constants.SPOTIFY_TERM_LENGTHS:
                add_spotify_user_data(
                    user_sp,
                    user,
                    top_tracks_flag=True,
                    top_artists_flag=True,
                    time_range=time_range,
                )

            # Save database session
            db.session.commit()

            return redirect(url_for("user_survey", username=current_user.username))

        except exceptions.UserAlreadyExistsError as exc:
            logger.warning("User already exists, redirecting to survey")
            return redirect(url_for("user_survey", username=str(exc)))

        except exceptions.NoUserData as exc:
            # session.clear()
            logger.error(f"No user spotify data for: {str(exc)}")
            return render_template(
                "error.html",
                error=f"No data associated with the given Spotify account.  "
                f"Please log out with the following link (https://www.spotify.com/logout/) and sign in with a more active account.  "
                f"If the Spotify account is not used regularly, then no listening trends are expected.",
            )

        except Exception as exc:
            # session.clear()
            logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
            return render_template(
                "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
            )

    elif request.method == "POST":
        try:
            # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens
            #  if you reuse a SpotifyOAuth object.
            sp_oauth = get_current_user_spotify_oath()
            auth_url = sp_oauth.get_authorize_url()
            print(auth_url)
            return redirect(auth_url)
        except Exception as exc:
            logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
            return render_template(
                "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
            )

    return redirect(url_for("index"))


@app.route("/show_user/")
@app.route("/show_user/<string:username>")
def show_user(username=None):
    logger.info("SHOW USER")
    try:
        if not username:
            logger.warning("No username")
            return render_template("error.html", error=f"Please add username to url")
        else:
            user = users.query_username(username)
            if not user:
                logger.error("No user")
                return render_template(
                    "error.html", error=f"No user exists given username: '{username}'"
                )
            else:
                sorted_top_tracks_short_term = query_sorted_top_tracks(
                    user.id, "short_term"
                )
                sorted_top_artists_short_term = query_sorted_top_artists(
                    user.id, "short_term"
                )

                sorted_top_tracks_medium_term = query_sorted_top_tracks(
                    user.id, "medium_term"
                )
                sorted_top_artists_medium_term = query_sorted_top_artists(
                    user.id, "medium_term"
                )

                sorted_top_tracks_long_term = query_sorted_top_tracks(
                    user.id, "long_term"
                )
                sorted_top_artists_long_term = query_sorted_top_artists(
                    user.id, "long_term"
                )

                return render_template(
                    "display_user.html",
                    username=username,
                    top_tracks_short_term=sorted_top_tracks_short_term,
                    top_artists_short_term=sorted_top_artists_short_term,
                    top_tracks_medium_term=sorted_top_tracks_medium_term,
                    top_artists_medium_term=sorted_top_artists_medium_term,
                    top_tracks_long_term=sorted_top_tracks_long_term,
                    top_artists_long_term=sorted_top_artists_long_term,
                )

    except Exception as exc:
        logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
        return render_template(
            "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
        )


@app.route("/user_survey/")
@app.route("/user_survey/<string:username>")
def user_survey(username=None):
    logger.info(f"USER SURVEY for username: '{username}'")
    try:
        if not username:
            logger.warning("No username")
            return render_template("error.html", error=f"Please add username to url")
        else:
            user = users.query_username(username)
            if not user:
                logger.error("No user")
                return render_template(
                    "error.html", error=f"No user exists given username: '{username}'"
                )
            else:
                sorted_top_tracks_short_term = query_sorted_top_tracks(
                    user.id, "short_term"
                )
                sorted_top_artists_short_term = query_sorted_top_artists(
                    user.id, "short_term"
                )

                sorted_top_tracks_medium_term = query_sorted_top_tracks(
                    user.id, "medium_term"
                )
                sorted_top_artists_medium_term = query_sorted_top_artists(
                    user.id, "medium_term"
                )

                sorted_top_tracks_long_term = query_sorted_top_tracks(
                    user.id, "long_term"
                )
                sorted_top_artists_long_term = query_sorted_top_artists(
                    user.id, "long_term"
                )

                (
                    sorted_top_artists_short_term,
                    sorted_top_tracks_short_term,
                    sorted_top_artists_medium_term,
                    sorted_top_tracks_medium_term,
                    sorted_top_artists_long_term,
                    sorted_top_tracks_long_term,
                ) = utils.remove_duplicate_survey_questions(
                    sorted_top_artists_short_term,
                    sorted_top_tracks_short_term,
                    sorted_top_artists_medium_term,
                    sorted_top_tracks_medium_term,
                    sorted_top_artists_long_term,
                    sorted_top_tracks_long_term,
                )

                qs = 5
                return render_template(
                    "survey_question.html",
                    username=username,
                    top_tracks_short_term=sorted_top_tracks_short_term[:qs],
                    top_artists_short_term=sorted_top_artists_short_term[:qs],
                    top_tracks_medium_term=sorted_top_tracks_medium_term[:qs],
                    top_artists_medium_term=sorted_top_artists_medium_term[:qs],
                    top_tracks_long_term=sorted_top_tracks_long_term[:qs],
                    top_artists_long_term=sorted_top_artists_long_term[:qs],
                )
    except Exception as exc:
        logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
        return render_template(
            "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
        )


@app.route("/save_survey/<string:username>", methods=["POST"])
def save_survey(username: str):
    logger.info("SAVE SURVEY")
    try:
        if request.method == "POST":
            print(f"Saving survey for {username}...")
            _save_survey_form(request.form, username)
            logger.info("SURVEY SAVE COMPLETE")
            return redirect(url_for("thank_you"))
        else:
            return render_template(
                "error.html", error="Can't save survey as GET request."
            )

    except Exception as exc:
        logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
        return render_template(
            "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
        )


def _save_survey_form(form: dict, username: str) -> None:
    """"""

    def _get_artist(txt: str) -> str:
        lst = txt.split("-")
        return lst[0]

    def _get_bool(txt: str) -> str:
        if re.findall("yes", txt):
            return "yes"
        elif re.findall("no", txt):
            return "no"
        else:
            raise RuntimeError("Error getting answer from survey form tags.")

    def _get_time_range(txt: str) -> str:
        if re.findall("short-term", txt):
            return "short_term"
        if re.findall("medium-term", txt):
            return "medium_term"
        if re.findall("long-term", txt):
            return "long_term"
        else:
            raise RuntimeError("Error getting time range from survey form tags.")

    def _regular_survey(key: str, value: str, user: users.Users):
        response_type = None
        artist = None
        response = None
        time_range = None

        if re.search("top-artist-local", key):
            response_type = "top-artist-local"
            artist = _get_artist(key)
            response = _get_bool(value)
            time_range = _get_time_range(key)
        elif re.search("top-artist", key):
            response_type = "top-artist"
            artist = _get_artist(key)
            response = _get_bool(value)
            time_range = _get_time_range(key)
        elif re.search("top-track-local", key):
            response_type = "top-track-local"
            artist = _get_artist(key)
            response = _get_bool(value)
            time_range = _get_time_range(key)
        elif re.search("top-track", key):
            response_type = "top-track"
            artist = _get_artist(key)
            response = _get_bool(value)
            time_range = _get_time_range(key)

        if user and artist and response_type and response:
            logger.info(
                f"User: {user} - Artist: {artist} - Response: {response} - Response Type: {response_type}"
            )
            new_survey = survey.add_survey(
                user.get_user_id(), artist, response_type, response, time_range,
            )
            db.session.add(new_survey)
            db.session.commit()

    def _user_info_survey(key: str, value: str, user: users.Users):
        question_type = None
        answer = None

        if "frequency" in key:
            question_type = "frequency"
            answer = value
        elif "music-represented" in key:
            question_type = "music-represented"
            answer = value
        elif "music-tastes-" in key:
            question_type = "music-tastes"
            answer = value
        elif "age" in key:
            question_type = "age"
            answer = value
        elif "location-name" in key:
            question_type = "location"
            answer = value
        elif "email-name" in key:
            question_type = "email"
            answer = value

        if user and question_type and answer:
            logger.info(
                f"User: {user} - Question Type: {question_type} - Answer: {answer}"
            )
            new_user_info = user_info.add_user_info(
                user.get_user_id(), question_type, answer
            )
            db.session.add(new_user_info)
            db.session.commit()

    def _save_seen_artists(key: str, value: str, user: users.Users):
        question_type = "seen-artist"
        answer = _get_artist(key)

        if value == "yes":
            logger.info(
                f"User: {user} - Question Type: {question_type} - Answer: {answer}"
            )
            if user and question_type and answer:
                new_user_info = user_info.add_user_info(
                    user.get_user_id(), question_type, answer
                )
                db.session.add(new_user_info)
                db.session.commit()

    # Start function here #

    if not isinstance(form, dict):
        raise RuntimeError("Error - form isn't a dictionary in save survey.")

    current_user = users.query_username(username)
    if not current_user:
        raise RuntimeError(
            f"Unable to find user: '{username}' in database. Please try again from the home screen."
        )

    for input_key, input_value in request.form.items():
        if (
            "top-artist-local" in input_key
            or "top-artist" in input_key
            or "top-track-local" in input_key
            or "top-track" in input_key
        ):
            _regular_survey(input_key, input_value, current_user)
        elif (
            "frequency" in input_key
            or "music-represented" in input_key
            or "music-tastes-" in input_key
            or "age" in input_key
            or "location-name" in input_key
            or "email-name" in input_key
        ):
            _user_info_survey(input_key, input_value, current_user)
        elif "seen-artist" in input_key:
            _save_seen_artists(input_key, input_value, current_user)
        else:
            raise RuntimeError("Error - Survey question type not located.")


# authorization-code-flow Step 2.
# Have your application request refresh and access tokens;
# Spotify returns access and refresh tokens
@app.route("/callback")
def callback():
    logger.info("CALLBACK")
    try:
        # Don't reuse a SpotifyOAuth object because they store token info and you could leak user tokens
        #  if you reuse a SpotifyOAuth object.
        sp_oauth = get_current_user_spotify_oath()
        session.clear()
        code = request.args.get("code")
        token_info = sp_oauth.get_access_token(code, check_cache=False)

        # Saving the access token along with all other token related info
        session["token_info"] = token_info

        return redirect(url_for("login"))

    except Exception as exc:
        logger.exception(f"{exc.__class__.__name__}: {str(exc)}")
        return render_template(
            "error.html", error=f"{exc.__class__.__name__}: {str(exc)}"
        )


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

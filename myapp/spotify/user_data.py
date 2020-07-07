"""Spotify data module"""
import requests
from typing import NamedTuple, List, Optional

import spotipy
import spotipy.util

from myapp.constants import (
    SAVED_TRACKS_PULL_TYPE,
    TOP_ARTISTS_PULL_TYPE,
    TOP_TRACKS_PULL_TYPE,
    FOLLOWED_ARTISTS_PULL_TYPE,
    READ_EMAIL_SCOPE,
    LIBRARY_READ_SCOPE,
    TOP_READ_SCOPE,
    FOLLOW_READ_SCOPE,
)
from myapp.spotify import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


class Track(NamedTuple):
    """"""

    uri: str
    name: str


class Artist(NamedTuple):
    """"""

    uri: str
    name: str


class DataPull(NamedTuple):
    """"""

    artists: List[Artist]
    tracks: List[Track]
    type: str


def get_current_user_spotify_oath() -> spotipy.oauth2.SpotifyOAuth:
    """"""
    scope = " ".join(
        [READ_EMAIL_SCOPE, LIBRARY_READ_SCOPE, TOP_READ_SCOPE, FOLLOW_READ_SCOPE]
    )
    spotify_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
        username="current-user",
    )
    if not spotify_oauth:
        raise RuntimeError(f"Failed to get current user Spotify OAuth.")
    else:
        return spotify_oauth


def get_authorized_spotify(auth_token=None) -> spotipy.Spotify:
    """"""
    if auth_token is None:
        raise RuntimeError("Valid Spotify authorization token required.")

    user_spotify = spotipy.Spotify(auth=auth_token)
    if not user_spotify:
        raise RuntimeError(f"Failed to get current user Spotify driver.")
    else:
        return user_spotify


# API_BASE = 'https://accounts.spotify.com'
#
# # Set this to True for testing but you probably want it set to False in production.
# SHOW_DIALOG = True
#
#
# def get_authorization_url() -> str:
#     """"""
#     scope = " ".join([READ_EMAIL_SCOPE, LIBRARY_READ_SCOPE, TOP_READ_SCOPE, FOLLOW_READ_SCOPE])
#     return f'{API_BASE}/authorize?scope={scope}&response_type=code&redirect_uri={REDIRECT_URI}&client_id={CLIENT_ID}&show_dialog={SHOW_DIALOG}'


def get_current_user_username(user_spotify):
    """"""
    return user_spotify.current_user().get("id")


def get_current_user_saved_tracks_data(
    user_spotify, limit: int = 20, offset: int = 0
) -> Optional[DataPull]:
    """ToDo: Fix this for offset"""
    if limit > 20:
        raise RuntimeError("Limit must be 20 or less")

    try:
        current_user_saved_tracks = user_spotify.current_user_saved_tracks(limit=limit)
    except requests.exceptions.HTTPError as exc:
        print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
        return
    except Exception as exc:
        print(f"Error: {exc.__class__.__name__} - {exc}")
        return

    artists = []
    tracks = []
    for item in current_user_saved_tracks["items"]:
        track = item["track"]
        tracks.append(Track(uri=track["uri"], name=track["name"]))

        for artist in track["artists"]:
            artists.append(Artist(uri=artist["uri"], name=artist["name"]))

    return DataPull(artists=artists, tracks=tracks, type=SAVED_TRACKS_PULL_TYPE)


def get_current_user_top_artists(
    user_spotify, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
) -> Optional[DataPull]:
    """ToDo: Fix this for offset"""
    if limit > 20:
        raise RuntimeError("Limit must be 20 or less")

    try:
        top_artists_data = user_spotify.current_user_top_artists(
            limit=limit, offset=offset, time_range=time_range
        )
    except requests.exceptions.HTTPError as exc:
        print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
        return
    except Exception as exc:
        print(f"Error: {exc.__class__.__name__} - {exc}")
        return

    artists = []
    for artist in top_artists_data["items"]:
        artists.append(Artist(uri=artist["uri"], name=artist["name"]))

    return DataPull(artists=artists, tracks=[], type=TOP_ARTISTS_PULL_TYPE)


def get_current_user_top_tracks(
    user_spotify, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
) -> Optional[DataPull]:
    """ToDo: Fix this for offset"""
    if limit > 20:
        raise RuntimeError("Limit must be 20 or less")

    try:
        top_tracks_data = user_spotify.current_user_top_tracks(
            limit=limit, offset=offset, time_range=time_range
        )
    except requests.exceptions.HTTPError as exc:
        print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
        return
    except Exception as exc:
        print(f"Error: {exc.__class__.__name__} - {exc}")
        return

    artists = []
    tracks = []
    for track in top_tracks_data["items"]:
        tracks.append(Track(uri=track["uri"], name=track["name"]))

        for artist in track["artists"]:
            artists.append(Artist(uri=artist["uri"], name=artist["name"]))

    return DataPull(artists=artists, tracks=tracks, type=TOP_TRACKS_PULL_TYPE)


def get_current_user_followed_artists(
    user_spotify, limit: int = 20, after: Optional[str] = None
) -> Optional[DataPull]:
    """ToDo: Fix this for offset"""
    if limit > 20:
        raise RuntimeError("Limit must be 20 or less")

    try:
        user_followed_data = user_spotify.current_user_followed_artists(
            limit=limit, after=after
        )
    except requests.exceptions.HTTPError as exc:
        print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
        return None
    except Exception as exc:
        print(f"Error: {exc.__class__.__name__} - {exc}")
        return None

    artists = []
    for artist in user_followed_data["artists"]["items"]:
        artists.append(Artist(uri=artist["uri"], name=artist["name"]))

    return DataPull(artists=artists, tracks=[], type=FOLLOWED_ARTISTS_PULL_TYPE)

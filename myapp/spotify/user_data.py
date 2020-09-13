"""Spotify data module"""
import requests
from typing import NamedTuple, List, Optional

import spotipy
import spotipy.util

from myapp.constants import (
    TOP_ARTISTS_PULL_TYPE,
    TOP_TRACKS_PULL_TYPE,
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
    scope = " ".join([READ_EMAIL_SCOPE, TOP_READ_SCOPE])
    spotify_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=scope,
        # cache_path="current-cache",
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


def get_current_user_username(user_spotify):
    """"""
    return user_spotify.current_user().get("id")


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

    if artists:
        return DataPull(artists=artists, tracks=[], type=TOP_ARTISTS_PULL_TYPE)

    return None


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

    if artists and tracks:
        return DataPull(artists=artists, tracks=tracks, type=TOP_TRACKS_PULL_TYPE)

    return None

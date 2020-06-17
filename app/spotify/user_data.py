"""User Profile module"""
import requests
from typing import NamedTuple, List, Optional

import spotipy
import spotipy.util

from app.constants import (
    SAVED_TRACKS_PULL_TYPE,
    TOP_ARTISTS_PULL_TYPE,
    TOP_TRACKS_PULL_TYPE,
    FOLLOWED_ARTISTS_PULL_TYPE,
    # READ_EMAIL_SCOPE,
    LIBRARY_READ_SCOPE,
    TOP_READ_SCOPE,
    FOLLOW_READ_SCOPE,
)
from app.spotify import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI


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


class UserData:
    """Interface to manage user Spotify data."""

    def __init__(self):
        self.user_spotify = spotipy.Spotify(auth=self._get_current_user_spotify_token())

    @staticmethod
    def _get_current_user_spotify_token():
        scope = " ".join([LIBRARY_READ_SCOPE, TOP_READ_SCOPE, FOLLOW_READ_SCOPE])
        token = spotipy.util.prompt_for_user_token(
            "current-user", scope, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Failed to authenticate user Spotify account.")
        else:
            return token

    def get_current_user_username(self):
        """"""
        return self.user_spotify.current_user().get("id")

    def get_current_user_saved_tracks_data(
        self, limit: int = 20, offset: int = 0
    ) -> Optional[DataPull]:
        """ToDo: Fix this for offset"""
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            current_user_saved_tracks = self.user_spotify.current_user_saved_tracks(
                limit=limit
            )
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
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ) -> Optional[DataPull]:
        """ToDo: Fix this for offset"""
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        print("Start")
        try:
            user_top_spotify = self.user_spotify
            print(user_top_spotify)
            top_artists_data = user_top_spotify.current_user_top_artists(
                limit=limit, offset=offset, time_range=time_range
            )
            print("1")
        except requests.exceptions.HTTPError as exc:
            print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
            return
        except Exception as exc:
            print(f"Error: {exc.__class__.__name__} - {exc}")
            return
        print("2")
        artists = []
        for artist in top_artists_data["items"]:
            artists.append(Artist(uri=artist["uri"], name=artist["name"]))
        print("1")
        return DataPull(artists=artists, tracks=[], type=TOP_ARTISTS_PULL_TYPE)

    def get_current_user_top_tracks(
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ) -> Optional[DataPull]:
        """ToDo: Fix this for offset"""
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_top_spotify = self.user_spotify
            top_tracks_data = user_top_spotify.current_user_top_tracks(
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
        self, limit: int = 20, after: Optional[str] = None
    ) -> Optional[DataPull]:
        """ToDo: Fix this for offset"""
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_followed_spotify = self.user_spotify
            user_followed_data = user_followed_spotify.current_user_followed_artists(
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

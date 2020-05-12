"""User Profile module"""
import requests
from typing import List, Optional

import spotipy
import spotipy.util

from spotify import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, Track, Artist, DataPull


class UserProfile:
    def __init__(self, username):
        self.username = username

        self.user_library_spotify = None
        self.user_top_spotify = None
        self.user_playlists_spotify = None
        self.user_followed_spotify = None

        self.saved_tracks: List[DataPull] = []
        self.top_artists: List[DataPull] = []
        self.top_tracks: List[DataPull] = []
        self.user_playlists: List[DataPull] = []
        self.followed_artists: List[DataPull] = []

    def _get_user_library_read_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username, "user-library-read", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def get_current_user_saved_tracks_data(self, limit: int = 20, offset: int = 0) -> None:
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_library_spotify = spotipy.Spotify(
                auth=self._get_user_library_read_token()
            )
            current_user_saved_tracks = user_library_spotify.current_user_saved_tracks(
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

        self.saved_tracks = DataPull(artists=artists, tracks=tracks)

    def _get_user_top_read_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username, "user-top-read", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def get_current_user_top_artists(
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ) -> None:
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_top_spotify = spotipy.Spotify(auth=self._get_user_top_read_token())
            top_artists_data = user_top_spotify.current_user_top_artists(
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

        self.top_artists = DataPull(artists=artists, tracks=[])

    def get_current_user_top_tracks(
        self, limit: int = 20, offset: int = 0, time_range: str = "medium_term"
    ) -> None:
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_top_spotify = spotipy.Spotify(auth=self._get_user_top_read_token())
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

        self.top_tracks = DataPull(artists=artists, tracks=tracks)

    def _get_playlist_read_private_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username,
            "playlist-read-private",
            CLIENT_ID,
            CLIENT_SECRET,
            REDIRECT_URI,
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def current_user_playlist_scan(self, limit: int = 10) -> None:
        try:
            # if limit > 50:
            #     print("Paganation is not setup. Defaulting to 50")
            #     limit = 50
            user_playlist_spotify = spotipy.Spotify(
                auth=self._get_playlist_read_private_token()
            )
            playlist_data = user_playlist_spotify.current_user_playlists(limit=limit)
        except requests.exceptions.HTTPError as exc:
            print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
            return
        except Exception as exc:
            print(f"Error: {exc.__class__.__name__} - {exc}")
            return

        artists = []
        tracks = []
        for playlist in playlist_data["items"]:
            playlist_data = user_playlist_spotify.playlist(
                playlist["id"], fields="tracks,next"
            )

            playlist_tracks = playlist_data["tracks"]
            for item in playlist_tracks["items"]:
                track = item["track"]

                tracks.append(Track(uri=track["uri"], name=track["name"]))

                for artist in track["artists"]:
                    artists.append(Artist(uri=artist["uri"], name=artist["name"]))

            # Get further pagenations
            # while tracks['next']:
            #         tracks = user_playlist_spotify.next(tracks)
            #         for track in tracks:
            #             track_uris.append(track["uri"])

        self.user_playlists = DataPull(artists=artists, tracks=tracks)

    def _get_user_follow_read_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username, "user-follow-read", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def get_current_user_followed_artists(
        self, limit: int = 20, after: Optional[str] = None
    ) -> None:
        if limit > 20:
            raise RuntimeError("Limit must be 20 or less")

        try:
            user_followed_spotify = spotipy.Spotify(
                auth=self._get_user_follow_read_token()
            )
            user_followed_data = user_followed_spotify.current_user_followed_artists(
                limit=limit, after=after
            )
        except requests.exceptions.HTTPError as exc:
            print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
            return
        except Exception as exc:
            print(f"Error: {exc.__class__.__name__} - {exc}")
            return

        artists = []
        for artist in user_followed_data["artists"]["items"]:
            artists.append(Artist(uri=artist["uri"], name=artist["name"]))

        self.followed_artists = DataPull(artists=artists, tracks=[])

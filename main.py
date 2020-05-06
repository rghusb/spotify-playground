"""Spotipy Playground"""
import requests
import json
from typing import List, NamedTuple, Optional

import spotipy
import spotipy.util


CLIENT_ID = "f0ae48ba465242f89ccbd7e3a9d0121b"
CLIENT_SECRET = "286882c16615498b9feeaff1e1418394"
REDIRECT_URI = "http://localhost:9080"


class Track(NamedTuple):
    """"""

    uri: str
    name: str


class Artist(NamedTuple):
    """"""

    uri: str
    name: str


class UserProfile:
    def __init__(self, username):
        self.username = username

        # self.spotify = spotipy.Spotify(auth=spotipy.util.prompt_for_user_token(
        #     "", "", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        # ))

        self.artists = {}
        self.tracks = {}

    def get_ordered_artists(self):
        return list(
            reversed(sorted(self.artists.values(), key=lambda item: item["count"]))
        )

    def get_ordered_tracks(self):
        return list(
            reversed(sorted(self.tracks.values(), key=lambda item: item["count"]))
        )

    def add_artists(self, new_artists: List[Artist]):
        for artist in new_artists:
            if artist.uri in self.artists:
                self.artists[artist.uri]["count"] += 1
            else:
                self.artists[artist.uri] = {
                    "uri": artist.uri,
                    "name": artist.name,
                    "count": 1,
                }

    def add_tracks(self, new_tracks: List[Track]):
        for track in new_tracks:
            if track.uri in self.tracks:
                self.tracks[track.uri]["count"] = 2
            else:
                self.tracks[track.uri] = {
                    "uri": track.uri,
                    "name": track.name,
                    "count": 1,
                }

    def _get_user_library_read_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username, "user-library-read", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def get_current_user_saved_tracks_data(self, limit: int = 20) -> None:
        user_library_spotify = spotipy.Spotify(auth=self._get_user_library_read_token())
        try:
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

        self.add_artists(artists)
        self.add_tracks(tracks)

    def _get_user_top_read_token(self) -> str:
        token = spotipy.util.prompt_for_user_token(
            self.username, "user-top-read", CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
        )
        if not token:
            raise RuntimeError(f"Can't get token for: {self.username}")
        else:
            return token

    def get_current_user_top_artists(
        self, limit: int = 20, time_range: str = "medium_term"
    ) -> None:
        user_top_spotify = spotipy.Spotify(auth=self._get_user_top_read_token())
        try:
            top_artists_data = user_top_spotify.current_user_top_artists(
                limit=limit, time_range=time_range
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

        self.add_artists(artists)

    def get_current_user_top_tracks(
        self, limit: int = 20, time_range: str = "medium_term"
    ) -> None:
        user_top_spotify = spotipy.Spotify(auth=self._get_user_top_read_token())
        try:
            top_tracks_data = user_top_spotify.current_user_top_tracks(
                limit=limit, time_range=time_range
            )
        except requests.exceptions.HTTPError as exc:
            print(f"HTTPError accessing Spotify API: {exc.__class__.__name__} - {exc}")
            return
        except Exception as exc:
            print(f"Error: {exc.__class__.__name__} - {exc}")
            return

        artists = []
        tracks = []
        print(top_tracks_data.keys())
        for track in top_tracks_data["items"]:
            tracks.append(Track(uri=track["uri"], name=track["name"]))

            for artist in track["artists"]:
                artists.append(Artist(uri=artist["uri"], name=artist["name"]))

        self.add_artists(artists)
        self.add_tracks(tracks)

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
        user_playlist_spotify = spotipy.Spotify(
            auth=self._get_playlist_read_private_token()
        )
        try:
            if limit > 50:
                print("Paganation is not setup. Defaulting to 50")
                limit = 50
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
            playlist_data = user_playlist_spotify.playlist(playlist['id'],fields="tracks,next")

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

        self.add_artists(artists)
        self.add_tracks(tracks)

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
        user_followed_spotify = spotipy.Spotify(auth=self._get_user_follow_read_token())
        try:
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

        self.add_artists(artists)


if __name__ == "__main__":
    user_profile = UserProfile("rghusbands")

    number_of_tracks = 50
    time = "medium_term"

    # user_profile.get_current_user_top_artists(number_of_tracks, time)
    # user_profile.get_current_user_top_tracks(number_of_tracks, time)
    # user_profile.get_current_user_saved_tracks_data(number_of_tracks)
    # user_profile.current_user_playlist_scan(1)
    # user_profile.get_current_user_followed_artists(20)

    # print(f"Ordered artists: {user_profile.get_ordered_artists()}\n")
    # print(f"Ordered tracks: {user_profile.get_ordered_tracks()}\n")

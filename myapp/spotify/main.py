""""""
import spotipy
from typing import List, Dict

# Local project imports
from myapp.spotify import user_data
from myapp.spotify.user_data import DataPull

from myapp import db


from myapp.models import (
    artists,
    users,
    top_artists,
    top_tracks,
)


def query_sorted_top_artists(
    user_id: str, time_range: str = "medium_term"
) -> List[Dict[str, str]]:
    """"""
    user_top_artists = top_artists.query_top_artists(user_id, time_range)
    top_artists_lis = []
    for assoc in user_top_artists.association:
        top_artists_lis.append(
            {"name": assoc.artists.name, "rank": assoc.rank,}
        )
    if top_artists_lis:
        return sorted(top_artists_lis, key=lambda i: i["rank"])
    else:
        return []


def query_sorted_top_tracks(
    user_id: str, time_range: str = "medium_term"
) -> List[Dict[str, str]]:
    """"""
    user_top_tracks = top_tracks.query_top_tracks(user_id, time_range)
    top_tracks_lis = []
    for assoc in user_top_tracks.association:
        top_tracks_lis.append(
            {"name": assoc.artists.name, "count": assoc.count, "rank": assoc.rank,}
        )
    if top_tracks_lis:
        return sorted(top_tracks_lis, key=lambda i: i["rank"])
    else:
        return []


def add_spotify_user_data(
    user_spotify: spotipy.Spotify,
    user: users.Users,
    top_tracks_flag=False,
    top_artists_flag=False,
    time_range="medium_term",
) -> None:
    """"""

    # Pull user's data
    number_of_tracks = 20

    if top_tracks_flag:
        top_tracks_pull = user_data.get_current_user_top_tracks(
            user_spotify, limit=number_of_tracks, time_range=time_range
        )
        if not top_tracks_pull:
            raise RuntimeError("No top tracks data to add.")
        _add_top_tracks(user, top_tracks_pull, time_range)

    if top_artists_flag:
        top_artists_pull = user_data.get_current_user_top_artists(
            user_spotify, number_of_tracks, 0, time_range
        )
        if not top_artists_pull:
            raise RuntimeError("No top artists data to add.")
        _add_top_artists(user, top_artists_pull, time_range)


def _add_top_tracks(user: users.Users, data_pull: DataPull, time_range: str) -> None:
    """"""
    top_tracks_table = top_tracks.add_top_tracks(user, time_range)

    for i, artist in enumerate(data_pull.artists):
        art_ = artists.add_artist(artist.name, artist.uri)

        association_query = top_tracks.query_top_tracks_artists_association(
            top_tracks_id=top_tracks_table.id, artists_id=art_.id
        )
        # Check if association already exists
        if association_query.count() > 0:
            existing_association = association_query.first()
            existing_association.count += 1
            db.session.add(existing_association)
        else:
            new_association = top_tracks.TopTracksArtistsAssociation(
                top_tracks=top_tracks_table, artists=art_, rank=i + 1
            )
            top_tracks_table.association.append(new_association)
            db.session.add(new_association)

    db.session.add(top_tracks_table)


def _add_top_artists(user: users.Users, data_pull: DataPull, time_range: str) -> None:
    """"""
    top_artists_table = top_artists.add_top_artists(user, time_range)

    for i, artist in enumerate(data_pull.artists):
        art_ = artists.add_artist(artist.name, artist.uri)
        new_association = top_artists.TopArtistsArtistsAssociation(
            top_artists=top_artists_table, artists=art_, rank=i + 1
        )
        top_artists_table.association.append(new_association)
        db.session.add(new_association)

    db.session.add(top_artists_table)

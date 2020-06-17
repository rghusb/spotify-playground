""""""
# Local project imports
from app import constants
from app.spotify.user_data import UserData, DataPull

from app import db


from app.models import (
    artists,
    # tracks,
    users,
    followed_artists,
    saved_tracks,
    top_artists,
    top_tracks,
)


def add_spotify_user_data(
    top_tracks_flag=False,
    top_artists_flag=False,
    saved_tracks_flag=False,
    followed_artists_flag=False,
) -> None:
    """"""

    # Pull user's data
    number_of_tracks = 20
    time = "medium_term"
    spotify_user_data = UserData()
    spotify_username = spotify_user_data.get_current_user_username()

    if not spotify_username:
        raise RuntimeError("Unable to access current user's username.")

    # Add user
    user = users.add_user(spotify_username)

    if top_tracks_flag:
        top_tracks_pull = spotify_user_data.get_current_user_top_tracks(
            limit=number_of_tracks, time_range=time
        )
        if not top_tracks_pull:
            raise RuntimeError("No top tracks data to add.")
        add_data_pull(user, top_tracks_pull)

    if top_artists_flag:
        top_artists_pull = spotify_user_data.get_current_user_top_artists(
            number_of_tracks, 0, time
        )
        if not top_artists_pull:
            raise RuntimeError("No top artists data to add.")
        add_data_pull(user, top_artists_pull)

    if saved_tracks_flag:
        saved_tracks_pull = spotify_user_data.get_current_user_saved_tracks_data(
            number_of_tracks, 0
        )
        if not saved_tracks_pull:
            raise RuntimeError("No saved tracks data to add.")
        add_data_pull(user, saved_tracks_pull)

    if followed_artists_flag:
        followed_artists_pull = spotify_user_data.get_current_user_followed_artists(
            20, None
        )
        if not followed_artists_pull:
            raise RuntimeError("No followed artists data to add.")
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
                top_tracks=top_tracks_table, artists=art_
            )
            top_tracks_table.association.append(new_association)
            db.session.add(new_association)

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

        association_query = saved_tracks.query_saved_tracks_artists_association(
            saved_tracks_id=saved_tracks_table.id, artists_id=art_.id
        )
        # Check if association already exists
        if association_query.count() > 0:
            existing_association = association_query.first()
            existing_association.count += 1
            db.session.add(existing_association)
        else:
            new_association = saved_tracks.SavedTracksArtistsAssociation(
                saved_tracks=saved_tracks_table, artists=art_
            )
            saved_tracks_table.association.append(new_association)
            db.session.add(new_association)

    db.session.add(saved_tracks_table)


def _add_followed_artists(user: users.Users, data_pull: DataPull) -> None:
    """"""
    followed_artists_table = followed_artists.add_followed_artists(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        followed_artists_table.artists.append(art_)

    db.session.add(followed_artists_table)

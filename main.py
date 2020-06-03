""""""
from app import db
from app import constants
from app.models import (
    top_tracks,
    top_artists,
    saved_tracks,
    followed_artists,
    artists,
    tracks,
    users,
)
from app.spotify.user_data import UserData, DataPull


def add_spotify_user_data(
    spotify_username: str,
    top_tracks_flag=False,
    top_artists_flag=False,
    saved_tracks_flag=False,
    followed_artists_flag=False,
) -> None:
    """"""
    # Add user
    user = users.add_user(spotify_username)

    # Pull user's data
    number_of_tracks = 20
    time = "medium_term"
    spotify_user_data = UserData(spotify_username)

    if top_tracks_flag:
        top_tracks_pull = spotify_user_data.get_current_user_top_tracks(
            limit=number_of_tracks, time_range=time
        )
        if not top_tracks_pull:
            print("No top tracks data to add.")
        add_data_pull(user, top_tracks_pull)

    if top_artists_flag:
        top_artists_pull = spotify_user_data.get_current_user_top_artists(
            number_of_tracks, 0, time
        )
        if not top_artists_pull:
            print("No top artists data to add.")
        add_data_pull(user, top_artists_pull)

    if saved_tracks_flag:
        saved_tracks_pull = spotify_user_data.get_current_user_saved_tracks_data(
            number_of_tracks, 0
        )
        if not saved_tracks_pull:
            print("No saved tracks data to add.")
        add_data_pull(user, saved_tracks_pull)

    if followed_artists_flag:
        followed_artists_pull = spotify_user_data.get_current_user_followed_artists(
            20, None
        )
        if not followed_artists_pull:
            print("No followed artists data to add.")
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
        top_tracks_table.artists.append(art_)

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
        saved_tracks_table.artists.append(art_)

    db.session.add(saved_tracks_table)


def _add_followed_artists(user: users.Users, data_pull: DataPull) -> None:
    """"""
    followed_artists_table = followed_artists.add_followed_artists(user)

    for artist in data_pull.artists:
        art_ = artists.add_artist(artist.name, artist.uri)
        followed_artists_table.artists.append(art_)

    db.session.add(followed_artists_table)


if __name__ == "__main__":
    """"""
    # try:
    print("Running...")
    add_spotify_user_data(
        "rghusbands",
        top_tracks_flag=True,
        top_artists_flag=True,
        saved_tracks_flag=True,
        followed_artists_flag=True,
    )
    # except Exception as err:
    #     print(f"{err.__class__.__name__}: {err}")
    #     print("*** Error ***")
    # else:
    print("Success!")

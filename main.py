""""""
from app import db
from app import constants
from app.models import top_artists
from app.models import users
from app.models import artists
from app.spotify.user_data import UserData, DataPull


def add_spotify_user_data(
    spotify_username: str,
    top_tracks=False,
    top_artists=False,
    saved_tracks=False,
    followed_artists=False,
) -> None:
    """"""
    # Add user
    user = users.add_user(spotify_username)

    # Pull user's data
    number_of_tracks = 20
    time = "medium_term"
    spotify_user_data = UserData(spotify_username)

    if top_tracks:
        top_tracks_pull = spotify_user_data.get_current_user_top_tracks(
            limit=number_of_tracks, time_range=time
        )
        if not top_tracks_pull:
            print("No top tracks data to add.")
        else:
            add_data_pull(user, top_tracks_pull)

    if top_artists:
        top_artists_pull = spotify_user_data.get_current_user_top_artists(
            number_of_tracks, 0, time
        )
        if not top_artists_pull:
            print("No top artists data to add.")
        else:
            add_data_pull(user, top_artists_pull)

    if saved_tracks:
        saved_tracks_pull = spotify_user_data.get_current_user_saved_tracks_data(
            number_of_tracks, 0
        )
        if not saved_tracks_pull:
            print("No saved tracks data to add.")
        else:
            add_data_pull(user, saved_tracks_pull)

    if followed_artists:
        followed_artists_pull = spotify_user_data.get_current_user_followed_artists(
            20, None
        )
        if not followed_artists_pull:
            print("No followed artists data to add.")
        else:
            add_data_pull(user, followed_artists_pull)

    db.session.add(user)
    db.session.commit()


def add_data_pull(user: users.Users, data_pull: DataPull) -> None:
    """"""
    if data_pull.type == constants.TOP_TRACKS_PULL_TYPE:
        raise NotImplemented(f"for data type: {data_pull.type}")
    elif data_pull.type == constants.TOP_ARTISTS_PULL_TYPE:
        _add_top_artists(user, data_pull)
    elif data_pull.type == constants.SAVED_TRACKS_PULL_TYPE:
        raise NotImplemented(f"for data type: {data_pull.type}")
    elif data_pull.type == constants.FOLLOWED_ARTISTS_PULL_TYPE:
        raise NotImplemented(f"for data type: {data_pull.type}")
    else:
        raise RuntimeError(
            f"Can't find matching database table for give data pull type: {data_pull.type}"
        )


def _add_top_tracks():
    """"""


def _add_top_artists(user: users.Users, data_pull: DataPull):
    """"""
    top_artists_table = top_artists.add_top_artists(user)

    for artist in data_pull.artists:
        art_ = artists.query_name(artist.name)
        if art_:
            print("Artist already exists")
        else:
            new_artist = artists.Artists(name=artist.name, uri=artist.uri)
            print(f"Artist added. Name: {artist.name} - URI: {artist.uri}")
            db.session.add(new_artist)
            top_artists_table.artists.append(new_artist)

    db.session.add(top_artists_table)


def _add_saved_tracks():
    """"""


def _add_followed_artists():
    """"""


if __name__ == "__main__":
    """"""
    # try:
    print("Running...")
    add_spotify_user_data("rghusbands", top_artists=True)
    # except Exception as err:
    #     print(f"{err.__class__.__name__}: {err}")
    #     print("*** Error ***")
    # else:
    print("Success!")

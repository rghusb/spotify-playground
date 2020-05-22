"""Main Spotipy Playground"""
from user_profile import UserProfile


if __name__ == "__main__":
    user_profile = UserProfile("rghusbands")

    number_of_tracks = 20
    time = "medium_term"

    user_profile.get_current_user_top_artists(number_of_tracks, 0, time)
    # user_profile.get_current_user_top_tracks(number_of_tracks, time)
    # user_profile.get_current_user_saved_tracks_data(number_of_tracks)
    # user_profile.current_user_playlist_scan(1)
    # user_profile.get_current_user_followed_artists(20)

    # print(f"Ordered artists: {user_profile.get_ordered_artists()}\n")
    # print(f"Ordered tracks: {user_profile.get_ordered_tracks()}\n")

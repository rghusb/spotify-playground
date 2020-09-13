"""Utility functions for myapp"""
from typing import Tuple, List


def remove_duplicate_survey_questions(
    sorted_top_artists_short_term,
    sorted_top_tracks_short_term,
    sorted_top_artists_medium_term,
    sorted_top_tracks_medium_term,
    sorted_top_artists_long_term,
    sorted_top_tracks_long_term,
) -> Tuple[List, List, List, List, List, List]:
    """"""

    def _clean_list(lst, seen):
        """"""
        new_lst = []
        for item in lst:
            name = item["name"]
            if name not in seen:
                new_lst.append(item)
                seen.append(name)

        return new_lst, seen

    seen_artists = []  # Empty list of seen artists to start

    # Short term
    sorted_top_artists_short_term, seen_artists = _clean_list(
        sorted_top_artists_short_term, seen_artists
    )
    sorted_top_tracks_short_term, seen_artists = _clean_list(
        sorted_top_tracks_short_term, seen_artists
    )

    # Medium term
    sorted_top_artists_medium_term, seen_artists = _clean_list(
        sorted_top_artists_medium_term, seen_artists
    )
    sorted_top_tracks_medium_term, seen_artists = _clean_list(
        sorted_top_tracks_medium_term, seen_artists
    )

    # Long term
    sorted_top_artists_long_term, seen_artists = _clean_list(
        sorted_top_artists_long_term, seen_artists
    )
    sorted_top_tracks_long_term, seen_artists = _clean_list(
        sorted_top_tracks_long_term, seen_artists
    )

    return (
        sorted_top_artists_short_term,
        sorted_top_tracks_short_term,
        sorted_top_artists_medium_term,
        sorted_top_tracks_medium_term,
        sorted_top_artists_long_term,
        sorted_top_tracks_long_term,
    )

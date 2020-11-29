"""Database Interface"""
from collections import Counter
import csv

from myapp import db
from flask import session

from myapp.models.user_info import UserInfo

# from myapp.models.users import Users
from myapp.models.survey import Survey


# Database create
def create_tables():
    db.create_all()


# Survey
def votes():
    count = db.session.query(Survey).count()
    yes_votes = db.session.query(Survey).filter_by(answer="yes").count()
    print(f"Total yes percentage: {(yes_votes/count)*100:.2f}%")
    print(f"Total no percentage: {100-(yes_votes / count) * 100:.2f}%")
    local_votes(yes_votes)
    print(f"\nPercentage of yes votes that are top tracks vs top artists:")
    yes_votes_top_artists(yes_votes)
    yes_votes_top_tracks(yes_votes)
    print(f"\nTime frames for yes votes short, medium, vs long term:")
    yes_votes_short_term()
    yes_votes_medium_term()
    yes_votes_long_term()


def local_votes(yes_votes):
    yes_votes_top_artist_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-artist-local")
        .count()
    )
    yes_votes_top_track_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-track-local")
        .count()
    )
    print(
        f"Percentage of yes votes that are local: {(yes_votes_top_artist_local+yes_votes_top_track_local)*100/yes_votes:.2f}%"
    )
    no_votes = db.session.query(Survey).filter_by(answer="no").count()
    no_votes_top_artist_local = (
        db.session.query(Survey)
        .filter_by(answer="no", question_type="top-artist-local")
        .count()
    )
    no_votes_top_track_local = (
        db.session.query(Survey)
        .filter_by(answer="no", question_type="top-track-local")
        .count()
    )
    print(
        f"Percentage of no votes that are local: {(no_votes_top_artist_local+no_votes_top_track_local)*100/no_votes:.2f}%"
    )


def yes_votes_top_artists(yes_votes):
    # count = db.session.query(Survey).count()
    yes_votes_non_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-artist")
        .count()
    )
    yes_votes_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-artist-local")
        .count()
    )
    ratio = (yes_votes_non_local + yes_votes_local) / yes_votes
    print(f"Top artists: {ratio * 100:.2f}%")
    return ratio


def yes_votes_top_tracks(yes_votes):
    # count = db.session.query(Survey).count()
    yes_votes_non_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-track")
        .count()
    )
    yes_votes_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", question_type="top-track-local")
        .count()
    )
    ratio = (yes_votes_non_local + yes_votes_local) / yes_votes
    print(f"Top tracks: {ratio*100:.2f}%")
    return ratio


def yes_votes_short_term():
    count = db.session.query(Survey).count()
    yes_votes = (
        db.session.query(Survey)
        .filter_by(answer="yes", time_frame="short_term")
        .count()
    )
    yes_votes_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", time_frame="short_term")
        .count()
    )
    ratio = (yes_votes + yes_votes_local) / count
    print(f"Short term: {ratio * 100:.2f}%")
    return ratio


def yes_votes_medium_term():
    count = db.session.query(Survey).count()
    yes_votes = (
        db.session.query(Survey)
        .filter_by(answer="yes", time_frame="medium_term")
        .count()
    )
    yes_votes_local = (
        db.session.query(Survey)
        .filter_by(answer="yes", time_frame="medium_term")
        .count()
    )
    ratio = (yes_votes + yes_votes_local) / count
    print(f"Medium term: {ratio * 100:.2f}%")
    return ratio


def yes_votes_long_term():
    count = db.session.query(Survey).count()
    yes_votes = (
        db.session.query(Survey).filter_by(answer="yes", time_frame="long_term").count()
    )
    yes_votes_local = (
        db.session.query(Survey).filter_by(answer="yes", time_frame="long_term").count()
    )
    ratio = (yes_votes + yes_votes_local) / count
    print(f"Long term: {ratio * 100:.2f}%")
    return ratio


def audiences():
    age_ranges()
    concert_frequency()
    music_tastes()


def age_ranges():
    ages = {}
    for item in db.session.query(UserInfo).filter_by(question_type="age"):
        ans = item.answer
        if ans in ages:
            ages[ans] += 1
        else:
            ages[ans] = 1
    print(f"\nAge range counter: {ages}")
    return ages


def concert_frequency():
    freq = {}
    for item in db.session.query(UserInfo).filter_by(question_type="frequency"):
        ans = item.answer
        if ans in freq:
            freq[ans] += 1
        else:
            freq[ans] = 1
    print(f"\nConcert frequency counter: {freq}")
    return freq


def music_tastes():
    tastes = {}
    for item in db.session.query(UserInfo).filter_by(question_type="music-tastes"):
        ans = item.answer
        if ans in tastes:
            tastes[ans] += 1
        else:
            tastes[ans] = 1
    print(f"\nMusic tastes counter: {tastes}")
    return tastes


def get_yes_votes(user_ids):
    answer = "yes"
    survey_results = []
    for user_id in user_ids:
        for survey_result in (
            db.session.query(Survey).filter_by(user_id=user_id, answer=answer).all()
        ):
            survey_results.append(survey_result)
    print(f"\nYes survey votes for given list of user ids: {survey_results}")


def get_no_votes(user_ids):
    answer = "no"
    for user_id in user_ids:
        for survey_result in (
            db.session.query(Survey).filter_by(user_id=user_id, answer=answer).all()
        ):
            print(survey_result)


def yes_votes_details():
    answer = "yes"
    local = Counter()
    non_local = Counter()

    for survey_result in db.session.query(Survey).filter_by(answer=answer).all():
        if (
            survey_result.question_type == "top-track-local"
            or survey_result.question_type == "top-artist-local"
        ):
            local[survey_result.question_artist_name] += 1
        else:
            non_local[survey_result.question_artist_name] += 1

    print("\nYes vote artists analysis:")
    print(f"Regular counter: {non_local}")
    print(f"Local counter: {local}")


def no_votes_details():
    answer = "no"
    no_local = Counter()
    no_non_local = Counter()

    for survey_result in db.session.query(Survey).filter_by(answer=answer).all():
        if (
            survey_result.question_type == "top-track-local"
            or survey_result.question_type == "top-artist-local"
        ):
            no_local[survey_result.question_artist_name] += 1
        else:
            no_non_local[survey_result.question_artist_name] += 1

    print("\nNo vote artists analysis:")
    print(f"Regular counter: {no_non_local}")
    print(f"Local counter: {no_local}")


"""DATA MIGRATION"""


def group_by_user_and_artist():
    """"""
    user_survey_data = {}
    for survey_result in db.session.query(Survey).all():
        user_id = survey_result.user_id
        artist_name = survey_result.question_artist_name
        question_type = survey_result.question_type
        answer = survey_result.answer
        time_frame = survey_result.time_frame

        if user_id not in user_survey_data:
            user_survey_data[user_id] = {}

        if artist_name not in user_survey_data[user_id]:
            user_survey_data[user_id][artist_name] = {"time_frame": time_frame}

        if question_type not in user_survey_data[user_id][artist_name]:
            user_survey_data[user_id][artist_name][question_type] = {}

        if answer not in user_survey_data[user_id][artist_name][question_type]:
            user_survey_data[user_id][artist_name][question_type][answer] = 1
        else:
            user_survey_data[user_id][artist_name][question_type][answer] += 1

    return user_survey_data


def user_info_by_user_id():
    """"""
    user_info_data = {}
    for survey_info in db.session.query(UserInfo).all():
        user_id = survey_info.user_id
        question_type = survey_info.question_type
        answer = survey_info.answer

        if user_id not in user_info_data:
            user_info_data[user_id] = {}

        if question_type in user_info_data[user_id] and (
            question_type == "seen-artist" or question_type == "music-tastes"
        ):
            user_info_data[user_id][question_type].append(answer)
        elif question_type == "seen-artist" or question_type == "music-tastes":
            user_info_data[user_id][question_type] = [answer]
        else:
            user_info_data[user_id][question_type] = answer

    return user_info_data


def _yes_or_no(user_artist_data, category):
    """"""
    actual = None
    local = None

    if category == "top-track":
        top_track = user_artist_data.get("top-track", {})
        if top_track:
            yes = top_track.get("yes", 0)
            no = top_track.get("no", 0)
            if yes > no:
                actual = "yes"
            elif no > yes:
                actual = "no"

        top_track_local = user_artist_data.get("top-track-local", {})
        if top_track_local:
            yes = top_track_local.get("yes", 0)
            no = top_track_local.get("no", 0)
            if yes > no:
                local = "yes"
            elif no > yes:
                local = "no"

    elif category == "top-artist":
        top_artist = user_artist_data.get("top-artist", {})
        if top_artist:
            yes = top_artist.get("yes", 0)
            no = top_artist.get("no", 0)
            if yes > no:
                actual = "yes"
            elif no > yes:
                actual = "no"

        top_artist_local = user_artist_data.get("top-artist-local", {})
        if top_artist_local:
            yes = top_artist_local.get("yes", 0)
            no = top_artist_local.get("no", 0)
            if yes > no:
                local = "yes"
            elif no > yes:
                local = "no"

    else:
        raise RuntimeError("Error with categories")

    return actual, local


def excel_output():
    """"""
    survey_data = group_by_user_and_artist()
    user_info_data = user_info_by_user_id()

    with open("survey_results.csv", "w") as csv_file:
        spreadsheet = csv.writer(csv_file, delimiter=",")

        headers = [
            "userId",
            "artist",
            "category",
            "timeFrame",
            "actualResponse",
            "localResponse",
            "seenLive",
            "age",
            "frequency",
            "musicTastes",
            "musicRepresentation",
            "alternative",
            "classical",
            "blues",
            "country",
            "dance",
            "electronic",
            "hip-hop/rap",
            "indie-pop",
            "jazz",
            "latin",
            "metal",
            "pop",
            "progressive",
            "r&b/soul",
            "reggae",
            "rock",
            "world",
        ]
        spreadsheet.writerow(headers)

        for user_id in survey_data:
            user_data = survey_data[user_id]

            for artist_name in survey_data[user_id]:
                user_artist_data = user_data[artist_name]

                category = None
                if (
                    "top-track" in user_artist_data
                    or "top-track-local" in user_artist_data
                ):
                    category = "top-track"
                elif (
                    "top-artist" in user_artist_data
                    or "top-artist-local" in user_artist_data
                ):
                    category = "top-artist"

                time_frame = user_artist_data["time_frame"]

                actual_response, local_response = _yes_or_no(user_artist_data, category)

                user_info = user_info_data.get(user_id, {})
                seen_artists = user_info.get("seen-artist", [])
                seen_artist = "yes" if artist_name in seen_artists else "no"
                age = user_info.get("age")
                frequency = user_info.get("frequency")
                music_tastes = user_info.get("music-tastes", [])
                music_representation = user_info.get("music-represented")

                row = [
                    user_id,
                    artist_name,
                    category,
                    time_frame,
                    actual_response,
                    local_response,
                    seen_artist,
                    age,
                    frequency,
                    music_representation,
                    "yes" if "alternative" in music_tastes else None,
                    "yes" if "classical" in music_tastes else None,
                    "yes" if "blues" in music_tastes else None,
                    "yes" if "country" in music_tastes else None,
                    "yes" if "dance" in music_tastes else None,
                    "yes" if "electronic" in music_tastes else None,
                    "yes" if "hip-hop/rap" in music_tastes else None,
                    "yes" if "indie-pop" in music_tastes else None,
                    "yes" if "jazz" in music_tastes else None,
                    "yes" if "latin" in music_tastes else None,
                    "yes" if "metal" in music_tastes else None,
                    "yes" if "pop" in music_tastes else None,
                    "yes" if "progressive" in music_tastes else None,
                    "yes" if "r&b/soul" in music_tastes else None,
                    "yes" if "reggae" in music_tastes else None,
                    "yes" if "rock" in music_tastes else None,
                    "yes" if "world" in music_tastes else None,
                ]
                spreadsheet.writerow(row)


def survey_throughput():
    created_user_ids = []
    for value in db.session.query(Survey.user_id).distinct():
        created_user_ids.append(value[0])

    completed_user_ids = []
    for value in db.session.query(UserInfo.user_id).distinct():
        unique_user_id = value[0]
        completed_user_ids.append(unique_user_id)

    print(f"Total created user ids: {len(created_user_ids)} - {created_user_ids}")
    print(f"Total completed surveys: {len(completed_user_ids)} - {completed_user_ids}")


"""  MAIN  """


if __name__ == "__main__":
    survey_throughput()

    # data = group_by_user_and_artist()
    # for user_id in data:
    #     for artist in data[user_id]:
    #         print(f"Artist: {artist} and Data: {data[user_id][artist]}")

    # excel_output()
    # print(user_info_by_user_id())

    # votes()
    # audiences()
    #
    # user_ids = [1]
    # get_yes_votes(user_ids)
    #
    # yes_votes_details()
    # no_votes_details()

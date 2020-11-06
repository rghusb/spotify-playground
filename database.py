"""Database Interface"""
from collections import Counter

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
    local(yes_votes)
    print(f"\nPercentage of yes votes that are top tracks vs top artists:")
    yes_votes_top_artists(yes_votes)
    yes_votes_top_tracks(yes_votes)
    print(f"\nTime frames for yes votes short, medium, vs long term:")
    yes_votes_short_term()
    yes_votes_medium_term()
    yes_votes_long_term()


def local(yes_votes):
    yes_votes_top_artist_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-artist-local").count()
    yes_votes_top_track_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-track-local").count()
    print(f"Percentage of yes votes that are local: {(yes_votes_top_artist_local+yes_votes_top_track_local)*100/yes_votes:.2f}%")
    no_votes = db.session.query(Survey).filter_by(answer="no").count()
    no_votes_top_artist_local = db.session.query(Survey).filter_by(answer="no", question_type="top-artist-local").count()
    no_votes_top_track_local = db.session.query(Survey).filter_by(answer="no", question_type="top-track-local").count()
    print(f"Percentage of no votes that are local: {(no_votes_top_artist_local+no_votes_top_track_local)*100/no_votes:.2f}%")


def yes_votes_top_artists(yes_votes):
    # count = db.session.query(Survey).count()
    yes_votes_non_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-artist").count()
    yes_votes_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-artist-local").count()
    ratio = (yes_votes_non_local + yes_votes_local) / yes_votes
    print(f"Top tracks: {ratio * 100:.2f}%")
    return ratio


def yes_votes_top_tracks(yes_votes):
    # count = db.session.query(Survey).count()
    yes_votes_non_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-track").count()
    yes_votes_local = db.session.query(Survey).filter_by(answer="yes", question_type="top-track-local").count()
    ratio = (yes_votes_non_local+yes_votes_local) / yes_votes
    print(f"Top tracks: {ratio*100:.2f}%")
    return ratio


def yes_votes_short_term():
    count = db.session.query(Survey).count()
    yes_votes = db.session.query(Survey).filter_by(answer="yes", time_frame="short_term").count()
    yes_votes_local = db.session.query(Survey).filter_by(answer="yes", time_frame="short_term").count()
    ratio = (yes_votes + yes_votes_local) / count
    print(f"Short term: {ratio * 100:.2f}%")
    return ratio


def yes_votes_medium_term():
    count = db.session.query(Survey).count()
    yes_votes = db.session.query(Survey).filter_by(answer="yes", time_frame="medium_term").count()
    yes_votes_local = db.session.query(Survey).filter_by(answer="yes", time_frame="medium_term").count()
    ratio = (yes_votes + yes_votes_local) / count
    print(f"Medium term: {ratio * 100:.2f}%")
    return ratio


def yes_votes_long_term():
    count = db.session.query(Survey).count()
    yes_votes = db.session.query(Survey).filter_by(answer="yes", time_frame="long_term").count()
    yes_votes_local = db.session.query(Survey).filter_by(answer="yes", time_frame="long_term").count()
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
        for survey_result in db.session.query(Survey).filter_by(user_id=user_id, answer=answer).all():
            survey_results.append(survey_result)
    print(f"\nYes survey votes for given list of user ids: {survey_results}")


def get_no_votes(user_ids):
    answer = "no"
    for user_id in user_ids:
        for survey_result in db.session.query(Survey).filter_by(user_id=user_id, answer=answer).all():
            print(survey_result)


def yes_votes_details():
    answer = "yes"
    local = Counter()
    non_local = Counter()

    for survey_result in db.session.query(Survey).filter_by(answer=answer).all():
        if survey_result.question_type == "top-track-local" or survey_result.question_type == "top-artist-local":
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
        if survey_result.question_type == "top-track-local" or survey_result.question_type == "top-artist-local":
            no_local[survey_result.question_artist_name] += 1
        else:
            no_non_local[survey_result.question_artist_name] += 1

    print("\nNo vote artists analysis:")
    print(f"Regular counter: {no_non_local}")
    print(f"Local counter: {no_local}")


if __name__ == "__main__":
    votes()
    audiences()

    user_ids = [1]
    get_yes_votes(user_ids)

    yes_votes_details()
    no_votes_details()

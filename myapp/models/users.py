""""""
from typing import Optional
from myapp import db
from myapp import exceptions

# from myapp.models.top_tracks import TopTracks
# from myapp.models.followed_artists import FollowedArtists
# from myapp.models.top_artists import TopArtists
# from myapp.models.saved_tracks import SavedTracks


class Users(db.Model):
    """"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column("username", db.String(64))
    display_name = db.Column("DisplayName", db.String(128))
    email = db.Column("Email", db.String(128))
    # spotify_username = db.Column("spotify_username", db.String(64))

    # saved_tracks_id = db.Column(db.Integer, db.ForeignKey("saved_tracks.id"))
    # saved_tracks = db.relationship("SavedTracks", backref="users")

    # top_artists_id = db.Column(db.Integer, db.ForeignKey("top_artists.id"))
    top_artists = db.relationship("TopArtists", backref="users")

    # top_tracks_id = db.Column(db.Integer, db.ForeignKey("top_tracks.id"))
    top_tracks = db.relationship("TopTracks", backref="users")

    # user_playlists_id = db.Column(db.Integer, db.ForeignKey("UserPlaylists.id"))
    # user_playlists = db.relationship(
    #     UserPlaylists, uselist=False, back_populates="users"
    # )

    # followed_artists_id = db.Column(db.Integer, db.ForeignKey("followed_artists.id"))
    # followed_artists = db.relationship("FollowedArtists", backref="users")

    def get_user_id(self):
        return self.id

    def get_username(self):
        return self.username


def add_user(username: str, display_name: Optional[str], email: Optional[str]) -> Users:
    """"""
    if query_username(username) is not None:
        # return query_username(username)  # testing
        raise exceptions.UserAlreadyExistsError(f"{username}")

    return Users(username=username, display_name=display_name, email=email)


def query_username(username: str) -> Optional[Users]:
    query = db.session.query(Users).filter_by(username=username)
    return query.first()

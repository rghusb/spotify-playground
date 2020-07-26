# """"""
# from typing import Optional
#
# from myapp import db
# from myapp.models.artists import Artists
# from myapp.models.users import Users
#
#
# followed_artists_artists_association = db.Table(
#     "followed_artists_artists",
#     db.metadata,
#     db.Column("followed_artists_id", db.Integer, db.ForeignKey("followed_artists.id")),
#     db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
# )
#
#
# class FollowedArtists(db.Model):
#     """"""
#
#     __tablename__ = "followed_artists"
#
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
#
#     artists = db.relationship(Artists, secondary=followed_artists_artists_association)
#
#
# def add_followed_artists(user: Users) -> FollowedArtists:
#     """"""
#     if query_followed_artists(user.get_user_id()) is not None:
#         raise RuntimeError(
#             f"Followed Artists table already exists for user: {user.get_username()}"
#         )
#
#     return FollowedArtists(users=user)
#
#
# def query_followed_artists(user_id: str) -> Optional[FollowedArtists]:
#     query = db.session.query(FollowedArtists).filter_by(user_id=user_id)
#     return query.first()

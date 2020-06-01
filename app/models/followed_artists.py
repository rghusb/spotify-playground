""""""
from app import db


# followed_artists_artists_association = db.Table(
#     "followed_artists_artists",
#     db.metadata,
#     db.Column("followed_artists_id", db.Integer, db.ForeignKey("followed_artists.id")),
#     db.Column("artists_id", db.Integer, db.ForeignKey("artists.id")),
# )


class FollowedArtists(db.Model):
    """"""

    __tablename__ = "followed_artists"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    # artists = db.relationship(Artists, secondary=followed_artists_artists_association)

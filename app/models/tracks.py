""""""
from typing import Optional

from app import db


class Tracks(db.Model):
    """"""

    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    uri = db.Column("uri", db.String(64))


def add_track(name: str, uri: str) -> Optional[Tracks]:
    """"""
    if query_name(name) is None:
        return None

    track = Tracks(name=name, uri=uri)
    db.session.add(track)
    db.session.commit()

    return track


def query_name(name: str) -> Optional[Tracks]:
    """"""
    query = db.session.query(Tracks).filter_by(name=name)
    # query = Tracks.query.get(1)
    return query.first()

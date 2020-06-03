""""""
from typing import Optional

from app import db


class Tracks(db.Model):
    """"""

    __tablename__ = "tracks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    uri = db.Column("uri", db.String(64))


def add_track(name: str, uri: str) -> Tracks:
    """"""
    existing_track = query_name(name)
    if existing_track:
        return existing_track

    print(f"Track added. Name: {name} - URI: {uri}")
    track = Tracks(name=name, uri=uri)
    db.session.add(track)
    return track


def query_name(name: str) -> Optional[Tracks]:
    """"""
    query = db.session.query(Tracks).filter_by(name=name)
    return query.first()

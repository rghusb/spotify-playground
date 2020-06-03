""""""
from typing import Optional

from app import db


class Artists(db.Model):
    """"""

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    uri = db.Column("uri", db.String(128))


def add_artist(name: str, uri: str) -> Artists:
    """"""
    existing_artist = query_name(name)
    if existing_artist:
        return existing_artist

    print(f"Artist added. Name: {name} - URI: {uri}")
    artist = Artists(name=name, uri=uri)
    db.session.add(artist)
    return artist


def query_name(name: str) -> Optional[Artists]:
    """"""
    query = db.session.query(Artists).filter_by(name=name)
    return query.first()

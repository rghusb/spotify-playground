""""""
from typing import Optional

from app import db


class Artists(db.Model):
    """"""

    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column("name", db.String(64))
    uri = db.Column("uri", db.String(128))


def add_artist(name: str, uri: str) -> Optional[Artists]:
    """"""
    if query_name(name) is not None:
        raise RuntimeError(f"Artist already exists with name: {name} - uri: {uri}")

    return Artists(name=name, uri=uri)


def query_name(name: str) -> Optional[Artists]:
    """"""
    query = db.session.query(Artists).filter_by(name=name)
    return query.first()

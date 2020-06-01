"""Database"""
from app import db


def create_tables():
    db.create_all()


if __name__ == "__main__":
    # print("hello")
    create_tables()

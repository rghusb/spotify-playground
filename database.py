"""Database Interface"""
from myapp import db
from flask import session
from myapp.models.user_info import UserInfo


def create_tables():
    db.create_all()


if __name__ == "__main__":
    # print("hello")
    create_tables()

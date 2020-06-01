from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
# app.config.from_object(Config)

db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# Initialize here for db.create_all()
# from app.models import artists, followed_artists, saved_tracks, top_artists, top_tracks, tracks, users
from app.models import artists, top_artists, tracks, users

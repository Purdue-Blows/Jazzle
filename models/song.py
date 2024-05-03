from enum import Enum
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.types import LargeBinary
from constants import Keys
from db import db
from models.genre import Genre

# POST ASKING ABOUT API
# https://www.jazzmusicarchives.com/forum/forum_posts.asp?TID=31557&PID=148922&#148922


# class Genres(Enum):
#     SWING = "swing"
#     BEBOP = "bebop"
#     COOL = "cool"
#     HARD_BOP = "hard bop"
#     MODAL = "modal"
#     FREE = "free"
#     LATIN = "latin"
#     FUSION = "fusion"
#     FUNK = "funk"
#     SOUL = "soul"
#     DIXIELAND = "dixieland"
#     GYPSY = "gypsy"
#     AFRO_CUBAN = "afro-cuban"
#     BOSSA_NOVA = "bossa nova"
#     SMOOTH = "smooth"
#     AVANT_GARDE = "avant-garde"
#     ETHNO = "ethno"
#     ACID = "acid"
#     POST_BOP = "post-bop"
#     THIRD_STREAM = "third stream"


# For the time being, I'm going to hard code ornithology
class Song(db.Model):
    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True)
    # To account for
    # "I'm a Cranky Old Yank in a Clanky Old Tank on the Streets of Yokohama with my Honolulu Mama Doin' Those Beat-o, Beat-o, Flat-On-My-Seat-o, Hirohito Blues."
    title = db.Column(db.String(155), unique=True, nullable=False)
    composer = db.Column(
        db.ForeignKey("artists.name"),
        nullable=False,
    )
    CheckConstraint("composer", "composer IS TRUE OR artists.composer IS TRUE"),
    form = db.Column(db.ForeignKey("forms.name"), nullable=False)
    performer = db.Column(
        db.ForeignKey("artists.name"),
        nullable=False,
    )
    CheckConstraint("performer", "performer IS TRUE OR artists.performer IS TRUE"),
    genre = db.Column(db.ForeignKey("genres.name"), nullable=False)
    key = db.Column(db.Enum(Keys), nullable=False)
    # Note that all of the files are stored on the server
    # The db just contains paths to them so they can be retrieved
    audio = db.Column(db.String(200), nullable=False)
    c_sheet_music = db.Column(db.String(200), nullable=False)
    bb_sheet_music = db.Column(db.String(200))
    eb_sheet_music = db.Column(db.String(200))
    bass_sheet_music = db.Column(db.String(200), nullable=False)
    selected = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        app: Flask,
        title,
        composer,
        form,
        performer,
        genre,
        key,
        audio,
        c_sheet_music,
        bb_sheet_music,
        eb_sheet_music,
        bass_sheet_music,
        update=True,
    ):
        """
        For creating new songs. If a unique or nullable constraint fails,
        an IntegrityError will be raised.
        """
        self.title = title
        self.composer = composer
        self.form = form
        self.performer = performer
        self.genre = genre
        self.key = key
        self.audio = audio
        self.c_sheet_music = c_sheet_music
        self.bb_sheet_music = bb_sheet_music
        self.eb_sheet_music = eb_sheet_music
        self.bass_sheet_music = bass_sheet_music
        if update:
            with app.app_context():
                with db.session() as session:
                    session.add(self)
                    session.commit()

    def write(self):
        """
        For writing a song to the database. If a unique or nullable constraint fails,
        an IntegrityError will be raised.
        """
        with db.session() as session:
            session.add(self)
            session.commit()

    def update(self):
        """
        For updating a song in the database. If a unique or nullable constraint fails,
        an IntegrityError will be raised.
        """
        with db.session() as session:
            session.commit()

    @staticmethod
    def retrieve(
        title: Optional[str] = None,
        composer: Optional[str] = None,
        form: Optional[str] = None,
        performer: Optional[str] = None,
        genre: Optional[str] = None,
        key: Optional[str] = None,
        selected: Optional[bool] = None,
    ):
        """
        For retrieving songs from the database based on specified parameters.
        """
        query = Song.query
        if title:
            query = query.filter(Song.title == title)
        if composer:
            query = query.filter(Song.composer == composer)
        if form:
            query = query.filter(Song.form == form)
        if performer:
            query = query.filter(Song.performer == performer)
        if genre:
            query = query.filter(Song.genre == genre)
        if key:
            query = query.filter(Song.key == key)
        if selected:
            query = query.filter(Song.selected == selected)
        return query.all()

    def __str__(self):
        return f"<Song: {self.title} - composer: {self.composer} - form: {self.form} - performer: {self.performer} - genre: {self.genre} - key: {self.key} - audio_clip: {self.audio_clip}>"

    def __repr__(self):
        return f"<Song: {self.title} - composer: {self.composer} - form: {self.form} - performer: {self.performer} - genre: {self.genre} - key: {self.key} - audio_clip: {self.audio_clip}>"

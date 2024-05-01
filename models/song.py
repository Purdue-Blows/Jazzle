from enum import Enum
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import LargeBinary
from db import db

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
    id = db.Column(db.Integer, primary_key=True)
    # To account for
    # "I'm a Cranky Old Yank in a Clanky Old Tank on the Streets of Yokohama with my Honolulu Mama Doin' Those Beat-o, Beat-o, Flat-On-My-Seat-o, Hirohito Blues."
    title = db.Column(db.String(155), unique=True, nullable=False)
    composer = db.Column(db.String(100), nullable=False)
    form = db.Column(db.String(100), nullable=False)
    performer = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    key = db.Column(db.String(50), nullable=False)
    audio = db.Column(db.LargeBinary, nullable=False)
    c_sheet_music_path = db.Column(db.String(200), nullable=False)
    bb_sheet_music_path = db.Column(db.String(200))
    eb_sheet_music_path = db.Column(db.String(200))
    bass_sheet_music_path = db.Column(db.String(200), nullable=False)
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
        audio_path,
        c_sheet_music_path,
        bb_sheet_music_path,
        eb_sheet_music_path,
        bass_sheet_music_path,
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
        self.audio_path = audio_path
        self.c_sheet_music_path = c_sheet_music_path
        self.bb_sheet_music_path = bb_sheet_music_path
        self.eb_sheet_music_path = eb_sheet_music_path
        self.bass_sheet_music_path = bass_sheet_music_path
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
        return f"{self.title}: {{'composer': {self.composer}, 'form': {self.form}, 'performer': {self.performer}, 'genre': {self.genre}, 'key': {self.key}, 'audio_clip': {self.audio_clip}}}"

    def __repr__(self):
        return f"<Song: {self.title} - composer: {self.composer} - form: {self.form} - performer: {self.performer} - genre: {self.genre} - key: {self.key} - audio_clip: {self.audio_clip}>"

from enum import Enum
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.types import LargeBinary, Text
from services.db import db


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )
    composer = db.Column(db.Boolean, default=False, nullable=False)
    performer = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(
        self, app: Flask, name: str, composer: bool, performer: bool, update=True
    ):
        self.name = name
        self.composer = composer
        self.performer = performer
        if update:
            with app.app_context():
                with db.session() as session:
                    session.add(self)
                    session.commit()

    def __repr__(self):
        return f"<Artist {self.name}, composer: {self.composer}, performer: {self.performer}>"

    def __str__(self):
        return f"<Artist {self.name}, composer: {self.composer}, performer: {self.performer}>"

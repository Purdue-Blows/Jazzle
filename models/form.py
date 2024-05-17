from enum import Enum
from typing import Optional
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.types import LargeBinary, Text
from services.db import db


class Form(db.Model):
    __tablename__ = "forms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
    )

    def __init__(self, app: Flask, name: str, update=True):
        self.name = name
        if update:
            with app.app_context():
                with db.session() as session:
                    session.add(self)
                    session.commit()

    def __repr__(self):
        return f"<Form {self.name}>"

    def __str__(self):
        return f"<Form {self.name}>"

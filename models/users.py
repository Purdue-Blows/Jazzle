from flask import Flask
from services.db import db
from flask_login import UserMixin
from constants import Roles
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    confirmed_at = db.Column(db.DateTime(), default=datetime.now())
    # Active discusses user activity; can be used for soft-deletion
    active = db.Column(db.Boolean())
    role = db.Column(db.Enum(Roles), nullable=False)

    def __init__(self, app: Flask, email: str, password: str, role, update=False):
        self.email = email
        self.password = password
        self.role = role
        if update:
            with app.app_context():
                db.session.add(self)
                db.session.commit()

    def __repr__(self):
        return f"<User {self.email} {self.role}>"

    def __str__(self):
        return f"<User {self.email} {self.role}>"

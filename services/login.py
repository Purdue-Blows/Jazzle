from flask_login import LoginManager

from models.users import User
from services.db import db


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).where(User.id == int(user_id)).first()

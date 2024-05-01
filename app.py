import os
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from sqlalchemy.exc import IntegrityError
from constants import (
    AUDIO_FILE_PATH,
    BASS_MUSIC_FILE_PATH,
    BB_MUSIC_FILE_PATH,
    C_MUSIC_FILE_PATH,
    EB_MUSIC_FILE_PATH,
)
from db import db
from flask_htmx import HTMX
from dotenv import load_dotenv
from models.song import Song
from auth import configure_auth

if not load_dotenv(os.path.join(os.getcwd(), ".env")):
    print("No .env file found")
    exit()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
# print(DB_USERNAME, DB_PASSWORD, DB_PORT, DB_NAME)

app = Flask(__name__)
htmx = HTMX(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
)

# initialize the app with the extension
db.init_app(app)
# create the database if not already created
with app.app_context():
    db.create_all()

# configure the admin interface
admin = Admin(app, name="jazzle", template_mode="bootstrap4")
# Add administrative views here

# Database administrative view
# class SongView(ModelView):
#     @expose('/download/<path:filename>')
#     def download_file(self, filename):
#         return send_from_directory("uploads", filename)

#     def _format_file_path(self, context, model, name):
#         path = getattr(model, name)
#         filename = path.split("/")[-1]  # Extract filename
#         audio_icon_url = url_for('static', filename="audio_icon.png")
#         return f'<a href="{self.get_url(window='inline', id=model.id)}download/{filename}"><img src="{audio_icon_url}" alt="Download Icon"></a>'

admin.add_view(ModelView(Song, db.session))

# Configure basic authentication
basic_auth = BasicAuth(app)
configure_auth(app)


# HELPERS
def update_jazzle():
    """
    Select a new jazzle  for the day, or, if all songs in the database
    have been selected, sends an email to the admin staff.
    """
    pass


# ROUTES
@app.route("/", methods=["GET"])
def home():
    if htmx:
        print("htmx is active!")
    return render_template("jazzle.html")


@app.route("/admin")
def admin():
    pass


if __name__ == "__main__":
    # TESTING: add a default song to the database
    try:
        title = "Ornithology"
        composer = "Charlie Parker"
        performer = "Charlie Parker"
        form = "ABAC"
        genre = "Bebop"
        key = "G"
        audio_path = AUDIO_FILE_PATH + "ornithology.mp3"
        # with open("static/ornithology.mp3", "rb") as f:
        #     audio = f.read()
        c_sheet_music_path = C_MUSIC_FILE_PATH + "ornithology_c.pdf"
        bb_sheet_music_path = BB_MUSIC_FILE_PATH + "ornithology_bb.pdf"
        eb_sheet_music_path = EB_MUSIC_FILE_PATH + "ornithology_eb.pdf"
        bass_sheet_music_path = BASS_MUSIC_FILE_PATH + "ornithology_bass.pdf"

        # with open("static/ornithology_c.pdf", "rb") as f:
        #     c_sheet_music = f.read()

        # with open("static/ornithology_bb.pdf", "rb") as f:
        #     bb_sheet_music = f.read()

        # with open("static/ornithology_eb.pdf", "rb") as f:
        #     eb_sheet_music = f.read()

        # with open("static/ornithology_bass.pdf", "rb") as f:
        #     bass_sheet_music = f.read()

        # Write ornithology to db
        ornithology = Song(
            app=app,
            title=title,
            composer=composer,
            form=form,
            performer=performer,
            genre=genre,
            key=key,
            audio_path=audio_path,
            c_sheet_music_path=c_sheet_music_path,
            bb_sheet_music_path=bb_sheet_music_path,
            eb_sheet_music_path=eb_sheet_music_path,
            bass_sheet_music_path=bass_sheet_music_path,
        )
    except IntegrityError as e:
        print(e)
    app.run(debug=True)

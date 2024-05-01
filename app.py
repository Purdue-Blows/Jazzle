import os
from flask import Flask, request, jsonify, render_template
from sqlalchemy.exc import IntegrityError
from db import db
from flask_htmx import HTMX
from dotenv import load_dotenv
from models.song import Song

# Ideally, you only get the first line of the melody
# For now, a 10 second cutoff works fine
CLIP_LENGTH = 10

if not load_dotenv(".env"):
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


@app.route("/")
def home():
    if htmx:
        print("htmx is active!")
    return render_template("index.html")


if __name__ == "__main__":
    # TESTING: add a default song to the database
    try:
        title = "Ornithology"
        composer = "Charlie Parker"
        performer = "Charlie Parker"
        form = "ABAC"
        genre = "Bebop"
        key = "G"
        audio = None
        with open("static/ornithology.mp3", "rb") as f:
            audio = f.read()
        c_sheet_music = None
        bb_sheet_music = None
        eb_sheet_music = None
        bass_sheet_music = None

        with open("static/ornithology_c.pdf", "rb") as f:
            c_sheet_music = f.read()

        with open("static/ornithology_bb.pdf", "rb") as f:
            bb_sheet_music = f.read()

        with open("static/ornithology_eb.pdf", "rb") as f:
            eb_sheet_music = f.read()

        with open("static/ornithology_bass.pdf", "rb") as f:
            bass_sheet_music = f.read()
    except IntegrityError as e:
        pass
    app.run(debug=True)

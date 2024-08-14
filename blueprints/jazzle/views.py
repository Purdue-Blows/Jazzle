import datetime
from mailbox import Message
import os
import zipfile
from flask import Blueprint, abort, flash, render_template, request, send_file, session
from constants import MAX_GUESSES, Roles, JAZZLE_STATIC_FILE_PATH
from models.users import User
from services.htmx import htmx
from services.mail import mail
from services.db import db
from models.song import Song
from sqlalchemy.sql.expression import func
from services.scheduler import scheduler
from jinja2_fragments import render_block
from flask_htmx import make_response
import PyPDF2

bp = Blueprint("jazzle", __name__, template_folder="templates")


# Cron triggers run at specific times
# This is commented out for development purposes; it can be uncommented when development is further along
# @scheduler.task("cron", id="update_jazzle", day="*", hour="0", minute="0")
def update_jazzle():
    """
    Select a new jazzle  for the day, or, if all songs in the database
    have been selected, sends an email to the admin staff.
    """
    # Update the jazzle for the day
    # with scheduler.app.app_context():
    old_song = db.session.query(Song).filter(Song.current == True).first()
    if old_song:
        old_song.current = False
        db.session.commit()

    # Select a random song that is not currently selected
    new_song = (
        db.session.query(Song)
        .filter(Song.selected == False)
        .order_by(func.random())
        .first()
    )

    # Update the selected and current flags for the chosen song
    if new_song:
        new_song.selected = True
        new_song.current = True
        db.session.commit()
        # num_not_selected = len(
        #     db.session.query(Song).filter(Song.selected == False).all()
        # )
        # match num_not_selected:
        #     # Send an email to the admin staff if all songs have been selected
        #     case 0:
        #         msg = Message(
        #             "All jazz songs in the database have been selected; make sure to add more songs to the database!",
        #             recipients=[
        #                 email for email in db.session.query(User.email).all()
        #             ],
        #         )
        #         msg.subject = "Only one day to add more jazz songs to the database!"
        #         mail.send(msg)
        #     case 7:
        #         msg = Message(
        #             "All jazz songs in the database have been selected; make sure to add more songs to the database!",
        #             recipients=[
        #                 email for email in db.session.query(User.email).all()
        #             ],
        #         )
        #         msg.subject = (
        #             "Only one week to add more jazz songs to the database!"
        #         )
        #         mail.send(msg)
        # else:
        #     # Send an email to the admin staff if all songs have been selected
        #     msg = Message(
        #         "All jazz songs in the database have been selected; make sure to add more songs to the database!",
        #         recipients=[email for email in db.session.query(User.email).all()],
        #     )
        #     msg.subject = "Could not select new song; NEED TO ADD MORE JAZZ SONGS TO THE DATABASE!"
        #     mail.send(msg)

    # Reset user guesses
    session["guesses"] = MAX_GUESSES


# ROUTES
@bp.route("/", methods=["GET", "POST"])
def home():
    # htmx.log_all()
    # session.permanent = True
    # song = db.session.query(Song).filter(Song.current == True).first()
    # if not song:
    #     abort(404)
    # song = ornithology
    if session.get("guesses", None) == None:
        session["guesses"] = MAX_GUESSES
        guesses = session["guesses"]
    else:
        guesses = session["guesses"]

    # if session.get("pitch", None) == None:
    #     session["pitch"] = "c"

    if session["guesses"] == 0:
        song = db.session.query(Song).filter(Song.current == True).first()
        return render_template(
            "song.html",
            title=song.title,
            poster=song.poster,
            audio=song.audio,
            id=song.id,
        )

    return render_template(
        "jazzle.html",
        guesses=guesses,
        # form=song.form,
        # genre=song.genre,
        # key=song.key,
        # time_signature=song.time_signature,
        # composer=song.composer,
        # performer=song.performer,
        # audio=song.audio,
        # title=song.title,
        # c_sheet_music=song.c_sheet_music,
        # bb_sheet_music=song.bb_sheet_music,
        # eb_sheet_music=song.eb_sheet_music,
        # bass_sheet_music=song.bass_sheet_music,
    )


@bp.route("/update-guess-count")
def update_guess_count():
    return str(session["guesses"]), 200, {"HX-Trigger": "beforeSwap"}


# @bp.route("/pitch", methods=["POST"])
# def pitch():
#     session["pitch"] = request.form.get("pitch")
#     return render_template("jazzle.html", guesses=session["guesses"])


@bp.route("/guess", methods=["POST"])
def guess():
    session["guesses"] -= 1
    song_guess = request.form.get("song")
    song = db.session.query(Song).filter(Song.current == True).first()
    if song_guess.lower() == song.title.lower() or session["guesses"] <= 0:
        session["guesses"] = 0

        # Combine PDFs
        # pdf_files = []
        # if song.c_sheet_music:
        #     print(song.c_sheet_music)
        #     pdf_files.append(
        #         os.path.join(
        #             BASE_FILE_PATH,
        #             f"c_sheet_music/{song.c_sheet_music}",
        #         )
        #     )
        # if song.bb_sheet_music:
        #     pdf_files.append(
        #         os.path.join(BASE_FILE_PATH, f"bb_sheet_music/{song.bb_sheet_music}")
        #     )
        # if song.eb_sheet_music:
        #     pdf_files.append(
        #         os.path.join(BASE_FILE_PATH, f"eb_sheet_music/{song.eb_sheet_music}")
        #     )
        # if song.bass_sheet_music:
        #     pdf_files.append(
        #         os.path.join(
        #             BASE_FILE_PATH, f"bass_sheet_music/{song.bass_sheet_music}"
        #         )
        #     )

        # merger = PyPDF2.PdfMerger()
        # for pdf_file in pdf_files:
        #     merger.append(pdf_file)

        # if not os.path.exists(os.path.join(BASE_FILE_PATH, "tmp")):
        #     os.makedirs(os.path.join(BASE_FILE_PATH, "tmp"))

        # merger.write(os.path.join(BASE_FILE_PATH, "tmp", f"{song.title}.pdf"))
        # merger.close()

        return (
            render_template(
                "song.html",
                title=song.title,
                poster=song.poster,
                audio=song.audio,
                id=song.id,
            ),
            202,
        )  # Returning a 202 status code to indicate that the answer is correct
    else:
        # Return the updated html to swap
        match session["guesses"]:
            case 7:
                # Update the form of the song
                # Retrieve guess_7 and update it's text
                # Retrieve the number of guesses and update them
                return render_template(
                    "partial.form.html",
                    form=song.form,
                    guesses=session["guesses"],
                )
            case 6:
                # Update the genre of the song
                return render_template(
                    "partial.genre.html",
                    genre=song.genre,
                    guesses=session["guesses"],
                )
            case 5:
                # Update the key of the song
                # if session["pitch"] == "bass":
                #     return f"""<img id="guess_5" src="static/images/{song.key}_bass.png" alt="A musical key" height="20%">"""
                return render_template(
                    "partial.key.html",
                    key=song.key.name,
                    clef="treble",
                    guesses=session["guesses"],
                )
            case 4:
                # Update the time signature of the song
                return render_template(
                    "partial.time_signature.html",
                    time_signature=song.time_signature.name,
                    guesses=session["guesses"],
                )
            case 3:
                # Update the composer of the song
                return render_template(
                    "partial.composer.html",
                    composer=song.composer,
                    guesses=session["guesses"],
                )

            case 2:
                # Update the performer of the song
                return render_template(
                    "partial.performer.html",
                    performer=song.performer,
                    guesses=session["guesses"],
                )
            case 1:
                # Update the audio clip of the song
                return render_template(
                    "partial.audio.html",
                    audio_clip=song.audio_clip,
                    guesses=session["guesses"],
                )

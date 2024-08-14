from flask import Blueprint, render_template, request
import os
import zipfile
from flask import flash, request, send_file

from models.song import Song

bp = Blueprint(
    "showcase",
    __name__,
    url_prefix="/showcase",
    template_folder="templates",
)


@bp.route("/", methods=["GET"])
def showcase():
    songs = Song.query.all()
    print(songs)
    return render_template("showcase.html", songs=songs)


@bp.route("/download", methods=["GET"])
def download():
    title = request.args.get("title")

    # The download logic is the same, except you need to append any filter params appropriately
    # Retrieve the song with the given id from the database
    song = Song.query.where(Song.title == title.lower()).first()
    if song is None:
        return flash("Sorry, we couldn't find that song!")

    if request.args.get("part"):
        title += "_" + request.get.args("part")
        # Eventually there will be more keys available...
        match request.get.args("part"):
            case "C":
                return send_file(song.c_sheet_music, as_attachment=True)
            case "Bb":
                return send_file(song.bb_sheet_music, as_attachment=True)
            case "Eb":
                return send_file(song.eb_sheet_music, as_attachment=True)
            case "Bass":
                return send_file(song.bass_sheet_music, as_attachment=True)

    # Download a zip of the files for the row given the paths
    zip_path = f"/tmp/{song.title}.zip"
    with zipfile.ZipFile(zip_path, "w") as zip_file:
        zip_file.write(song.audio, os.path.basename(song.audio))
        zip_file.write(song.c_sheet_music, os.path.basename(song.c_sheet_music))
        if song.bb_sheet_music:
            zip_file.write(song.bb_sheet_music, os.path.basename(song.bb_sheet_music))
        if song.eb_sheet_music:
            zip_file.write(song.eb_sheet_music, os.path.basename(song.eb_sheet_music))
        zip_file.write(song.bass_sheet_music, os.path.basename(song.bass_sheet_music))
    return send_file(zip_path, as_attachment=True)

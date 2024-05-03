import os
import zipfile

# from typing import override
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField
from flask_admin.contrib.sqla import ModelView
from flask_basicauth import BasicAuth
from sqlalchemy.exc import IntegrityError
from constants import (
    AUDIO_FILE_PATH,
    BASS_MUSIC_FILE_PATH,
    BB_MUSIC_FILE_PATH,
    C_MUSIC_FILE_PATH,
    EB_MUSIC_FILE_PATH,
    Keys,
    Roles,
)
from flask_login import current_user, LoginManager, login_user, logout_user
from db import db
from flask_htmx import HTMX
from dotenv import load_dotenv
from models.artists import Artist
from models.form import Form
from models.genre import Genre
from models.song import Song
from models.users import User
from auth import configure_auth
from wtforms import SelectField
import os
from flask import send_file

if not load_dotenv(os.path.join(os.getcwd(), ".env")):
    print("No .env file found")
    exit()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
# print(DB_USERNAME, DB_PASSWORD, DB_PORT, DB_NAME)

app = Flask(__name__)
htmx = HTMX(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
)
app.config["SECRET_KEY"] = SECRET_KEY

# initialize the app with the extension
db.init_app(app)

# create the database if not already created
with app.app_context():
    db.create_all()

# Set up login
# - Login page for admin
# - Simple permissions (role-based) for models
# - Store and retrieve the current user credentials; that's more difficult
login_manager = LoginManager(app)


def url_has_allowed_host_and_scheme(url, allowed_hosts, require_https=False):
    """
    Return ``True`` if the url uses an allowed host and a safe scheme.

    Always return ``False`` on an empty url.

    If ``require_https`` is ``True``, only 'https' will be considered a valid
    scheme, as opposed to 'http' and 'https' with the default, ``False``.

    Note: "True" doesn't entail that a URL is "safe". It may still be e.g.
    quoted incorrectly. Ensure to also use django.utils.encoding.iri_to_uri()
    on the path component of untrusted URLs.
    """
    if url is not None:
        url = url.strip()
    if not url:
        return False
    if allowed_hosts is None:
        allowed_hosts = set()
    elif isinstance(allowed_hosts, str):
        allowed_hosts = {allowed_hosts}
    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return url_has_allowed_host_and_scheme(
        url, allowed_hosts, require_https=require_https
    ) and url_has_allowed_host_and_scheme(
        url.replace("\\", "/"), allowed_hosts, require_https=require_https
    )


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).where(User.id == int(user_id)).first()


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.query(User).where(User.email == email).first()
        if user and user.password == password:
            if not login_user(user):
                flash("That account is not active")
                return render_template("login.html")
            # next = request.args.get("next")
            # print(next)
            # if not url_has_allowed_host_and_scheme(next, request.host):
            #     return abort(400)
            return redirect("/admin")
        else:
            flash("Invalid email or password.")
    return render_template("login.html")


@app.route("/admin/logout", methods=["GET"])
def admin_logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("admin_login"))


# @app.route("/admin")
# def admin_index():
#     return render_template("/admin/index.html")


# configure the admin interface
admin = Admin(app, name="jazzle", template_mode="bootstrap4")
# Add administrative views here


# Database administrative view
# - Admin-specific routes
# - Dropdown for search
# - Make the paths icons and expose a downloadable path
class UserView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and (
                current_user.role == Roles.ADMIN
                or current_user.role == Roles.SUPER_ADMIN
            )
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for("admin.login"), next=request.url)


class SuperUserView(ModelView):
    def is_accessible(self):
        return (
            current_user.is_active
            and current_user.is_authenticated
            and current_user.role == Roles.SUPER_ADMIN
        )

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for("admin.login"), next=request.url)


class SongView(UserView):
    @app.route("/download/<int:id>", methods=["GET"])
    def download(id):
        # Retrieve the song with the given id from the database
        song = Song.query.get(id)
        if song is None:
            return "Song not found"

        # Download a zip of the files for the row given the paths
        zip_path = f"/tmp/{song.title}.zip"
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(song.audio, os.path.basename(song.audio))
            zip_file.write(song.c_sheet_music, os.path.basename(song.c_sheet_music))
            if song.bb_sheet_music:
                zip_file.write(
                    song.bb_sheet_music, os.path.basename(song.bb_sheet_music)
                )
            if song.eb_sheet_music:
                zip_file.write(
                    song.eb_sheet_music, os.path.basename(song.eb_sheet_music)
                )
            zip_file.write(
                song.bass_sheet_music, os.path.basename(song.bass_sheet_music)
            )
        return send_file(zip_path, as_attachment=True)

    column_searchable_list = [
        "title",
        "composer",
        "performer",
    ]
    column_filters = [
        "genre",
        "key",
        "selected",
    ]
    column_descriptions = dict(
        selection="Whether the song has been selected for jazzle yet"
    )
    column_extra_row_actions = [
        EndpointLinkRowAction(
            "fa fa-download",
            endpoint="download",
            title="Download Files",
            url_args=dict(id="id"),
        ),
    ]
    # v: view, c: context, m: model, n: name
    column_formatters = dict(
        audio=lambda v, c, m, n: "✅" if m.audio else "❌",
        c_sheet_music=lambda v, c, m, n: "✅" if m.c_sheet_music else "❌",
        bb_sheet_music=lambda v, c, m, n: "✅" if m.bb_sheet_music else "❌",
        eb_sheet_music=lambda v, c, m, n: "✅" if m.eb_sheet_music else "❌",
        bass_sheet_music=lambda v, c, m, n: "✅" if m.bass_sheet_music else "❌",
    )

    # Note: as far as I could tell, images can't be easily rendered using the below method
    # So I opted for just an action button + download options instead
    column_list = [
        "selected",
        "title",
        "key",
        "genre",
        "form",
        "composer",
        "performer",
        "audio",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
    ]

    # def validate_file(form, field):
    #     file = field.data
    #     if file is not None:
    #         # Perform virus scan or any other file validation here
    #         # You can use a library like ClamAV or VirusTotal API for virus scanning
    #         # Raise an exception if the file is not valid
    #         if not is_valid_file(file):
    #             raise ValidationError("Invalid file")

    form_extra_fields = {
        "genre": SelectField(
            "Genre",
            choices=lambda: [
                (f.name, f.name) for f in db.session.query(Genre.name).all()
            ],
        ),
        "form": SelectField(
            "Form",
            choices=lambda: [
                (f.name, f.name) for f in db.session.query(Form.name).all()
            ],
        ),
        "composer": SelectField(
            "Composer",
            choices=lambda: [
                (f.name, f.name)
                for f in db.session.query(Artist.name).where(Artist.composer == True)
            ],
        ),
        "performer": SelectField(
            "Performer",
            choices=lambda: [
                (f.name, f.name)
                for f in db.session.query(Artist.name).where(Artist.performer == True)
            ],
        ),
        "audio": FileUploadField(
            "Audio File",
            base_path=AUDIO_FILE_PATH,
            allowed_extensions=["mp3"],
            # validators=[validate_file],
        ),
        "c_sheet_music": FileUploadField(
            "C Sheet Music",
            base_path=C_MUSIC_FILE_PATH,
            allowed_extensions=["pdf"],
            # validators=[validate_file],
        ),
        "bb_sheet_music": FileUploadField(
            "Bb Sheet Music",
            base_path=BB_MUSIC_FILE_PATH,
            allowed_extensions=["pdf"],
            # validators=[validate_file],
        ),
        "eb_sheet_music": FileUploadField(
            "Eb Sheet Music",
            base_path=EB_MUSIC_FILE_PATH,
            allowed_extensions=["pdf"],
            # validators=[validate_file],
        ),
        "bass_sheet_music": FileUploadField(
            "Bass Sheet Music",
            base_path=BASS_MUSIC_FILE_PATH,
            allowed_extensions=["pdf"],
            # validators=[validate_file],
        ),
    }

    form_columns = {
        "title",
        "key",
        "genre",
        "form",
        "composer",
        "performer",
        "audio",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
    }

    form_rules = [
        "title",
        "key",
        "genre",
        "form",
        "composer",
        "performer",
        "audio",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
    ]


admin.add_view(SongView(Song, db.session))
# Generic model view for genres, forms, and artists
admin.add_view(UserView(Genre, db.session))
admin.add_view(UserView(Form, db.session))
admin.add_view(UserView(Artist, db.session))
admin.add_view(SuperUserView(User, db.session))

# Configure basic authentication
basic_auth = BasicAuth(app)
configure_auth(app)


# HELPERS
# I'll implement this last
def update_jazzle():
    """
    Select a new jazzle  for the day, or, if all songs in the database
    have been selected, sends an email to the admin staff.
    """
    pass


# ROUTES
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("jazzle.html")


@app.route("/showcase", methods=["GET"])
def showcase():
    return render_template("showcase.html")


if __name__ == "__main__":
    # TESTING: add a default song to the database
    try:
        title = "Ornithology"
        artist = Artist(
            app, name="Charlie Parker", composer=True, performer=True, update=False
        )
        form = Form(app, name="ABAC", update=False)
        genre = Genre(app, name="Bebop", update=False)
        key = Keys.G
        audio_path = AUDIO_FILE_PATH + "ornithology.mp3"
        c_sheet_music_path = C_MUSIC_FILE_PATH + "ornithology_c.pdf"
        bb_sheet_music_path = BB_MUSIC_FILE_PATH + "ornithology_bb.pdf"
        eb_sheet_music_path = EB_MUSIC_FILE_PATH + "ornithology_eb.pdf"
        bass_sheet_music_path = BASS_MUSIC_FILE_PATH + "ornithology_bass.pdf"

        # Write ornithology to db
        ornithology = Song(
            app=app,
            title=title,
            composer=artist.name,
            form=form.name,
            performer=artist.name,
            genre=genre.name,
            key=key,
            audio=audio_path,
            c_sheet_music=c_sheet_music_path,
            bb_sheet_music=bb_sheet_music_path,
            eb_sheet_music=eb_sheet_music_path,
            bass_sheet_music=bass_sheet_music_path,
        )
    except IntegrityError as e:
        print(e)
    app.run(debug=True)

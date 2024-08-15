from datetime import timedelta
import os
import tempfile

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    request,
    render_template,
    url_for,
)
from flask_basicauth import BasicAuth
from flask_login import LoginManager
from blueprints.jazzle.views import bp as jazzle_bp
from blueprints.showcase.views import bp as showcase_bp
from blueprints.jazzle_data.views import bp as jazzle_data_bp
from constants import (
    AUDIO_FILE_PATH,
    JAZZLE_STATIC_FILE_PATH,
    BASS_MUSIC_FILE_PATH,
    BB_MUSIC_FILE_PATH,
    C_MUSIC_FILE_PATH,
    EB_MUSIC_FILE_PATH,
    POSTER_FILE_PATH,
    Keys,
    Roles,
    TimeSignatures,
)
from models.users import User
from services.mail import mail
from services.htmx import htmx
from services.db import db
from services.auth import basic_auth
from services.login import login_manager
from flask_htmx import HTMX
from dotenv import load_dotenv
from models.artists import Artist
from models.form import Form
from models.genre import Genre
from models.song import Song
from services.auth import configure_auth
import os
import os
import zipfile
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from wtforms import BooleanField, SelectField, ValidationError
from services.db import db
from constants import (
    AUDIO_FILE_PATH,
    BASS_MUSIC_FILE_PATH,
    BB_MUSIC_FILE_PATH,
    C_MUSIC_FILE_PATH,
    EB_MUSIC_FILE_PATH,
    Roles,
)
from models.artists import Artist
from models.form import Form
from models.genre import Genre
from models.song import Song
from models.users import User
from flask_admin import Admin, expose
from flask_admin import helpers as admin_helpers
from flask_admin.model.template import macro, EndpointLinkRowAction, LinkRowAction
from flask_admin.form import FileUploadInput, FileUploadField
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, LoginManager, login_user, logout_user

from models.users import User
from services.login import login_manager
from services.db import db
from services.scheduler import scheduler
from pydub import AudioSegment

if not load_dotenv(os.path.join(os.getcwd(), ".env")):
    print("No .env file found")
    exit()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
# print(DB_USERNAME, DB_PASSWORD, DB_PORT, DB_NAME)

app = Flask(__name__)
# late Initialization of HTMX
htmx.init_app(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{DB_USERNAME}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}"
)
app.config["SECRET_KEY"] = SECRET_KEY
app.config["SCHEDULER_API_ENABLED"] = True

# late initialization of the db
db.init_app(app)

# create the database if not already created
with app.app_context():
    db.create_all()

# late initialization of basic authentication
basic_auth.init_app(app)
configure_auth(app)

# late initialization of the login manager
login_manager.init_app(app)

# late initialization of scheduling
scheduler.init_app(app)

scheduler.start()

# late initialization of mail
mail.init_app(app)
app.config["MAIL_DEFAULT_SENDER"] = MAIL_DEFAULT_SENDER

# initialize admin


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


# @bp.route("/admin")
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
                return redirect(url_for("admin_login"))


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
                return redirect(url_for("admin_login"))


class SongView(UserView):
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
                return redirect(url_for("admin_login"))

    @app.route("/download/<int:id>", methods=["GET"])
    def download(id):
        # Retrieve the song with the given id from the database
        song = Song.query.get(id)
        if song is None:
            return "Song not found"

        # Download a zip of the files for the row given the paths
        zip_path = f"/tmp/{song.title}.zip"
        with zipfile.ZipFile(zip_path, "w") as zip_file:
            zip_file.write(f"blueprints/{song.audio}", os.path.basename(song.audio))
            zip_file.write(
                f"blueprints/{song.c_sheet_music}", os.path.basename(song.c_sheet_music)
            )
            if song.bb_sheet_music:
                zip_file.write(
                    f"blueprints/{song.bb_sheet_music}",
                    os.path.basename(song.bb_sheet_music),
                )
            if song.eb_sheet_music:
                zip_file.write(
                    f"blueprints/{song.eb_sheet_music}",
                    os.path.basename(song.eb_sheet_music),
                )
            zip_file.write(
                f"blueprints/{song.bass_sheet_music}",
                os.path.basename(song.bass_sheet_music),
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
        "time_signature",
        "form",
        "selected",
        "current",
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
        audio_clip=lambda v, c, m, n: "✅" if m.audio_clip else "❌",
        c_sheet_music=lambda v, c, m, n: "✅" if m.c_sheet_music else "❌",
        bb_sheet_music=lambda v, c, m, n: "✅" if m.bb_sheet_music else "❌",
        eb_sheet_music=lambda v, c, m, n: "✅" if m.eb_sheet_music else "❌",
        bass_sheet_music=lambda v, c, m, n: "✅" if m.bass_sheet_music else "❌",
        poster=lambda v, c, m, n: "✅" if m.poster else "❌",
    )

    # Note: as far as I could tell, images can't be easily rendered using the below method
    # So I opted for just an action button + download options instead
    column_list = [
        "selected",
        "current",
        "title",
        "key",
        "genre",
        "time_signature",
        "form",
        "composer",
        "performer",
        "audio",
        "audio_clip",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
        "poster",
    ]

    # def validate_file(form, field):
    #     file = field.data
    #     if file is not None:
    #         # Perform virus scan or any other file validation here
    #         # You can use a library like ClamAV or VirusTotal API for virus scanning
    #         # Raise an exception if the file is not valid
    #         if not is_valid_file(file):
    #             raise ValidationError("Invalid file")

    def create_model(self, form):
        audio_file = form.audio.data

        if not audio_file:
            return  # No file uploaded, skip validation

        try:
            # Open the audio file with pydub
            audio = AudioSegment.from_mp3(audio_file)

            # Export the audio file before trimming
            audio.export(os.path.join(AUDIO_FILE_PATH, audio_file.filename))

            # Extract the first 10 seconds (10000 milliseconds)
            trimmed_audio = audio[:10000]

            # Generate a unique filename with extension
            filename, extension = os.path.splitext(audio_file.filename)
            unique_filename = f"{filename}_clip{extension}"

            # Save the trimmed audio to the configured base path
            audio_clip_path = os.path.join(AUDIO_FILE_PATH, unique_filename)
            trimmed_audio.export(audio_clip_path)

            form.c_sheet_music.data.save(
                os.path.join(
                    C_MUSIC_FILE_PATH, form.c_sheet_music.data.filename.lower()
                )
            )
            form.bb_sheet_music.data.save(
                os.path.join(
                    BB_MUSIC_FILE_PATH, form.bb_sheet_music.data.filename.lower()
                )
            )
            form.eb_sheet_music.data.save(
                os.path.join(
                    EB_MUSIC_FILE_PATH, form.eb_sheet_music.data.filename.lower()
                )
            )
            form.bass_sheet_music.data.save(
                os.path.join(
                    BASS_MUSIC_FILE_PATH, form.bass_sheet_music.data.filename.lower()
                )
            )
            form.poster.data.save(
                os.path.join(POSTER_FILE_PATH, form.poster.data.filename.lower())
            )

            # Create the database instance
            title = form.title.data
            composer = form.composer.data
            performer = form.performer.data
            music_form = form.form.data
            genre = form.genre.data
            key = form.key.data
            time_signature = form.time_signature.data
            audio_path = form.audio.data.filename
            c_sheet_music_path = form.c_sheet_music.data.filename.lower()
            bb_sheet_music_path = form.bb_sheet_music.data.filename.lower()
            eb_sheet_music_path = form.eb_sheet_music.data.filename.lower()
            bass_sheet_music_path = form.bass_sheet_music.data.filename.lower()
            poster_path = form.poster.data.filename.lower()
            selected = form.selected.data
            current = form.current.data

            # Write ornithology to db
            song = Song(
                app=app,
                title=title,
                composer=composer,
                form=music_form,
                performer=performer,
                genre=genre,
                key=key,
                time_signature=time_signature,
                audio=audio_path,
                c_sheet_music=c_sheet_music_path,
                bb_sheet_music=bb_sheet_music_path,
                eb_sheet_music=eb_sheet_music_path,
                bass_sheet_music=bass_sheet_music_path,
                poster=poster_path,
                selected=selected,
                current=current,
            )
            return song

        except Exception as e:
            print(e)
            return False

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
        "poster": FileUploadField(
            "Poster",
            base_path=POSTER_FILE_PATH,
            allowed_extensions=["png", "jpg", "jpeg"],
        ),
        "current": BooleanField(),
        "selected": BooleanField(),
    }

    form_columns = {
        "title",
        "key",
        "genre",
        "time_signature",
        "form",
        "composer",
        "performer",
        "audio",
        # "audio_clip",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
        "poster",
        "current",
        "selected",
    }

    form_rules = [
        "title",
        "key",
        "genre",
        "form",
        "time_signature",
        "composer",
        "performer",
        "audio",
        # "audio_clip",
        "c_sheet_music",
        "bb_sheet_music",
        "eb_sheet_music",
        "bass_sheet_music",
        "poster",
        "current",
        "selected",
    ]


admin.add_view(SongView(Song, db.session))
# Generic model view for genres, forms, and artists
admin.add_view(UserView(Genre, db.session))
admin.add_view(UserView(Form, db.session))
admin.add_view(UserView(Artist, db.session))
admin.add_view(SuperUserView(User, db.session))


# Register blueprints
app.register_blueprint(showcase_bp)
app.register_blueprint(jazzle_bp)
app.register_blueprint(jazzle_data_bp)
# print(app.url_map)

# Maybe I should look into Model View Controller to avoid this complexity of HTML swapping?
# @app.route("/search/<string:query, string:title, string:composer, string:performer, enum:key, string:genre, string:form, enum:time_signature, bool:selected>", methods=["GET"])
# def search():
#     # Returns "Posters" of the results
#     # By default you can query title, composer, and performer
#     query = request.args.query
#     # With advanced search, you can query much more
#     title = request.args.title
#     # Another row below
#     composer = request.args.composer
#     performer = request.args.performer

#     key = request.args.key
#     genre = request.args.genre
#     form = request.args.form
#     time_signature = request.args.time_signature
#     selected = request.args.selected
#     db.session.query(Song).where(Song.)
#     pass

# @app.route("/advanced_search")
# def advanced_search():
#     # html for advanced search
#     # I need it so when ANYTHING in the form changes, the form submits
#     adv_search_html = f"""
#     <form id="search" hx-get="/search" hx-target="#results">
#         <div class="flex flex-row justify-center">
#             <input
#                 id="title"
#                 class="border-2"
#                 placeholder="Title!"
#             />
#         </div>
#         <div class="flex flex-row justify-center">
#             <input
#                 id="composer"
#                 class="border-2"
#                 placeholder="Composer!"
#             />
#             <input
#                 id="performer"
#                 class="border-2"
#                 placeholder="Performer!"
#             />
#         </div>
#         <div class="flex flex-row justify-center">
#             <select
#                 id="key"
#                 class="bg-transparent ml-2 font-extrabold outline"
#             >
#                 {[f"<option value={key}>{key}</option>" for key in Keys]}
#             </select>
#             <select
#                 id="genre"
#                 class="bg-transparent ml-2 font-extrabold outline"
#             >
#                 {[f"<option value={genre}>{genre}</option>" for genre in db.session.query(Genre.name).all()]}
#             </select>
#             <select
#                 id="form"
#                 class="bg-transparent ml-2 font-extrabold outline"
#             >
#                 {[f"<option value={form}>{form}</option>" for form in db.session.query(Form.name).all()]}
#             </select>
#             <select
#                 id="time_signature"
#                 class="bg-transparent ml-2 font-extrabold outline"
#             >
#                 {[f"<option value={time_signature}>{time_signature}</option>" for time_signature in TimeSignatures]}
#             </select>
#             <select
#                 id="selected"
#                 class="bg-transparent ml-2 font-extrabold outline"
#             >
#                 <option value="true">True</option>
#                 <option value="false">False</option>
#             </select>
#     </form>
#     <div class="flex flex-row justify-center>
#         <h2
#         hx-get="/advanced_search"
#         hx-target="#advanced_search"
#         class="font-extrabold opacity-80"
#         >
#         Advanced Search
#         </h2>
#     </div>
#     """
#     pass

# @app.route("/key/<string:key>", methods=["GET"])
# def key(key):
#     pass


# @app.route("/clef/<string:key>", methods=["GET"])
# def clef(key):
#     pass


# @app.route("/time_signature/<string:time_sig>", methods=["GET"])
# def time_signature(time_sig):
#     pass


# TODO: left off on downloads + cookies (I want key to be stored in cookies so it can be accessed everywhere)
# Maybe I make it a one time prompt and if it's set it's set?


# It feels strange to be returning html like this;
# it also doesn't seem like it follows locality of behavior
# @app.route("/navbar", methods=["GET"])
# def navbar():
#     navbar_html = """
#     <nav class="navbar navbar-expand-lg navbar-light bg-black">
#         <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
#             <span class="navbar-toggler-icon"></span>
#         </button>
#         <div class="collapse navbar-collapse" id="navbarNav">
#             <ul class="navbar-nav">
#                 <li class="nav-item active">
#                     <a class="nav-link" href="/">Jazzle</a>
#                 </li>
#                 <li class="nav-item">
#                     <a class="nav-link" href="/showcase">Showcase</a>
#                 </li>
#             </ul>
#         </div>
#     </nav>
#     """
#     return navbar_html


if __name__ == "__main__":
    # TESTING: add a default song to the database
    # Song.add_default(app)
    app.run(debug=True)

# Ideally, you only get the first line of the melody
# For now, a 10 second cutoff works fine
import base64
from enum import Enum
import os


CLIP_LENGTH = 10

BASE_STATIC_FILE_PATH = "static/"
JAZZLE_STATIC_FILE_PATH = "jazzle_data/static/"
AUDIO_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "audio/"
C_MUSIC_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "c_sheet_music/"
BB_MUSIC_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "bb_sheet_music/"
EB_MUSIC_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "eb_sheet_music/"
BASS_MUSIC_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "bass_sheet_music/"
POSTER_FILE_PATH = JAZZLE_STATIC_FILE_PATH + "posters/"
AUDIO_ICON = None
MAX_GUESSES = 8
with open(
    os.path.join(os.getcwd(), "static/images/audio_icon.svg"), "rb"
) as image_file:
    AUDIO_ICON = base64.b64encode(image_file.read()).decode()
SHEET_MUSIC_ICON = "static/images/sheet_music_icon.png"
with open(
    os.path.join(os.getcwd(), "static/images/sheet_music_icon.svg"), "rb"
) as image_file:
    SHEET_MUSIC_ICON = base64.b64encode(image_file.read()).decode()


class Keys(Enum):
    c = "C"
    csh = "C#"
    db = "Db"
    d = "D"
    dsh = "D#"
    eb = "Eb"
    e = "E"
    esh = "E#"
    f = "F"
    fsh = "F#"
    gb = "Gb"
    g = "G"
    gsh = "G#"
    ab = "Ab"
    a = "A"
    ash = "A#"
    bb = "Bb"
    b = "B"


class TimeSignatures(Enum):
    FOUR_FOUR = "4_4"
    THREE_FOUR = "3_4"
    THREE_EIGHT = "3_8"
    TWO_FOUR = "2_4"
    TWO_TWO = "2_2"
    SIX_EIGHT = "6_8"
    FIVE_FOUR = "5_4"
    FIVE_EIGHT = "5_8"
    SEVEN_FOUR = "7_4"
    SEVEN_EIGHT = "7_8"
    NINE_EIGHT = "9_8"
    NINE_FOUR = "9_4"
    ELEVEN_EIGHT = "11_8"
    ELEVEN_FOUR = "11_4"
    TWELVE_EIGHT = "12_8"
    THIRTEEN_EIGHT = "13_8"
    THIRTEEN_FOUR = "13_4"


class Roles(Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "superadmin"

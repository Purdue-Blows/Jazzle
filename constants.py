# Ideally, you only get the first line of the melody
# For now, a 10 second cutoff works fine
import base64
from enum import Enum
import os


CLIP_LENGTH = 10

BASE_FILE_PATH = "jazzle_data/"
AUDIO_FILE_PATH = BASE_FILE_PATH + "audio/"
C_MUSIC_FILE_PATH = BASE_FILE_PATH + "c_sheet_music/"
BB_MUSIC_FILE_PATH = BASE_FILE_PATH + "bb_sheet_music/"
EB_MUSIC_FILE_PATH = BASE_FILE_PATH + "eb_sheet_music/"
BASS_MUSIC_FILE_PATH = BASE_FILE_PATH + "bass_sheet_music/"
AUDIO_ICON = None
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
    C = "C"
    CS = "C#"
    Db = "Db"
    D = "D"
    DS = "D#"
    Eb = "Eb"
    E = "E"
    ES = "E#"
    F = "F"
    FS = "F#"
    Gb = "Gb"
    G = "G"
    GS = "G#"
    Ab = "Ab"
    A = "A"
    AS = "A#"
    Bb = "Bb"
    B = "B"


class Roles(Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "superadmin"

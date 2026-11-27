import re
import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# APIs
MUSIC_API_KEY = getenv("MUSIC_API_KEY", "")
RITESH_API_BASE = "https://api.riteshyt.in"
# Aarush Support (apni khud ki music API) — download mein backup,
# Ritesh uske baad backup. Key .env mein AARUSH_API_KEY se aati hai.
AARUSH_API_BASE = getenv("AARUSH_API_BASE", "https://aarush-support-api.hostless.app")
AARUSH_API_KEY = getenv("AARUSH_API_KEY", "")
# Yuki API — download mein pehli pasand (audio), Ritesh dusra backup.
# Key .env mein YUKI_API_KEY se aati hai.
YUKI_API_BASE = getenv("YUKI_API_BASE", "https://music.yukiapi.site")
YUKI_API_KEY = getenv("YUKI_API_KEY", "")
DRX_API_BASE = "https://apidrx-music.vercel.app/api"

OWNER_USERNAME = getenv("OWNER_USERNAME", "Mee_Aarush")
BOT_USERNAME = getenv("BOT_USERNAME", "Ishanimusice_bot")
BOT_NAME = getenv("BOT_NAME", "Ishani")
ASSUSERNAME = getenv("ASSUSERNAME", "THEDRXNET")

MONGO_DB_URI = getenv("MONGO_DB_URI", None)
MONGO_DB_URL = getenv("MONGO_DB_URL", None)

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 17000))
LOGGER_ID = int(getenv("LOGGER_ID", 0))
OWNER_ID = int(getenv("OWNER_ID", 7659846392))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", None)
HEROKU_API_KEY = getenv("HEROKU_API_KEY", None)

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/shoaib910385/Mytidalmusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")
GIT_TOKEN = getenv("GIT_TOKEN", "")

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/thedrxnet")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/drx_supportchat")

AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))

SERVER_PLAYLIST_LIMIT = int(getenv("SERVER_PLAYLIST_LIMIT", "3000"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "2500"))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "")

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)
STRING6 = getenv("STRING_SESSION6", None)
STRING7 = getenv("STRING_SESSION7", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

START_IMG_URL = getenv("START_IMG_URL", "https://ishani-music.ashubhai8935.workers.dev/img/start.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://ishani-music.ashubhai8935.workers.dev/img/start.jpg")
PLAYLIST_IMG_URL = "https://telegra.ph/file/d723f4c80da157fca1678.jpg"
STATS_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/start.jpg"
TELEGRAM_AUDIO_URL = "https://ishani-music.ashubhai8935.workers.dev/img/tunes.jpg"
TELEGRAM_VIDEO_URL = "https://ishani-music.ashubhai8935.workers.dev/img/tunes.jpg"
STREAM_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/stream.jpg"
SOUNCLOUD_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/stream.jpg"
YOUTUBE_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/stream.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/tunes.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/tunes.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://ishani-music.ashubhai8935.workers.dev/img/tunes.jpg"

def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL url.")
if SUPPORT_CHAT and not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT url.")
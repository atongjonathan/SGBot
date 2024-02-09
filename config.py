import os
from dotenv import load_dotenv


load_dotenv("config.env")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
DB_CHANNEL = os.environ.get('DB_CHANNEL')
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
MUSICXMATCH_API_KEY = os.environ.get("MUSICXMATCH_API_KEY")

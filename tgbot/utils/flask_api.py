from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import json
import telebot
from .functions import download
from tgbot.utils.database import Database
from tgbot.utils.spotify import Spotify
from tgbot.handlers.song_handler import SongHandler
load_dotenv("config.env")
users_json = os.environ.get("USERS")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DB_CHANNEL = os.environ.get("DB_CHANNEL")
app = Flask(__name__)
auth = HTTPBasicAuth()
bot = telebot.TeleBot(TOKEN)
song_handler = SongHandler(bot)
spotify = Spotify()
database = Database()
try:
    if users_json:
        users = json.loads(users_json)
    else:
        users = {}
except json.JSONDecodeError:
    users = {}


# Verify username and password
@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


@app.route('/', methods=['GET'])
def start():
    return "<h1><i>Welcome to the Spotify SG Bot API.</i></h2>"

# Protected route


@app.route('/song', methods=['POST'])
@auth.login_required
def callback():
    kwargs = request.json
    kwargs["chat_id"] = DB_CHANNEL
    track_url = kwargs["track_url"]
    track_details = spotify.get_chosen_song(track_url) 
    kwargs["performer"] = ", ".join(track_details["artists"])
    kwargs["title"] = track_details["name"]  
    kwargs["reply_markup"] = kwargs["hashtag"] = ""
    is_download_successfull = download(track_link=kwargs["track_url"],
                                       cwd=str(kwargs["chat_id"]))
    if is_download_successfull:
        try:
            song = song_handler.send_download(**kwargs)
            data = song.json["audio"]
            data["performer"] = kwargs["performer"]
            data["title"] = kwargs["title"]
            file_info = bot.get_file(data["file_id"])
            data["performer"] = ", ".join(track_details["artists"])
            data["title"] = track_details["name"]
            data["message_id"] = song.message_id
            database.insert_json_data(data, "audio")
            url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
                TOKEN, file_info.file_path)
            return jsonify({"url": url}), 200
        except Exception as e:
            return jsonify({"error": e, "url": None}), 500
    # return jsonify({"error": "Download Unsuccessful!"}), 500


def run_api():
    app.run(host='0.0.0.0', port=80)

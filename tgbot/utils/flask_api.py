from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from dotenv import load_dotenv
import os
import json
import telebot
from .functions import download
from tgbot.handlers.song_handler import SongHandler
load_dotenv("config.env")
users_json = os.environ.get("USERS")
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DB_CHANNEL = os.environ.get("DB_CHANNEL")
app = Flask(__name__)
auth = HTTPBasicAuth()
bot = telebot.TeleBot(TOKEN)
song_handler = SongHandler(bot)
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
    return jsonify({"message": "Welcome to the Spotify SG Bot API."})

# Protected route


@app.route('/song', methods=['POST'])
@auth.login_required
def callback():
    kwargs = request.json
    kwargs["chat_id"] = DB_CHANNEL
    kwargs["reply_markup"] = kwargs["title"] = kwargs["performer"] = kwargs["hashtag"] = ""
    is_download_successfull = download(track_link=kwargs["track_url"],
                                       cwd=str(kwargs["chat_id"]))
    if is_download_successfull:
        try:
            song = song_handler.send_download(**kwargs)
            data = song.json["audio"]
            file_info = bot.get_file(data["file_id"])

            url = 'https://api.telegram.org/file/bot{0}/{1}'.format(
                TOKEN, file_info.file_path)
            return jsonify({"url": url}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    # return jsonify({"error": "Download Unsuccessful!"}), 500


def run_api():
    app.run(host='0.0.0.0', port=8000)

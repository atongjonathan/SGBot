from flask import Flask
from threading import Thread

app = Flask(__name__)


@app.route('/')
def index():
    return "Bot is Running"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()

# howto keepalive

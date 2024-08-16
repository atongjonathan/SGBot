from tgbot.utils.flask_api import run_api
from threading import Thread



def run():
    run_api()


def keep_alive():
    t = Thread(target=run)
    t.start()

# howto keepalive

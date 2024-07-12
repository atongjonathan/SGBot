# handlers
from tgbot.handlers.callback_handler import CallbackHandler
# middleware
from tgbot.middlewares.antiflood_middleware import AntiFloodMiddleware
from tgbot.middlewares.query_middleware import QueryMiddleware
from tgbot.utils import keyboard, database
import time
from tgbot.handlers.artist_handler import ArtistHandler
from tgbot.handlers.song_handler import SongHandler
from tgbot.handlers.vars import Vars

# config
from tgbot.config import TOKEN

import telebot
import billboard
from keep_alive import keep_alive

import os
bot = telebot.TeleBot(TOKEN, parse_mode="markdown", use_class_middlewares=True)

logging = telebot.logging
logging.basicConfig(format="SGBot | %(asctime)s | %(levelname)s | %(module)s | %(lineno)s | %(message)s", level=logging.INFO, handlers=[
    logging.StreamHandler(),
    logging.FileHandler("logs.txt")
])
logger = logging.getLogger(__name__)


link_regex = "(https?:\\/\\/)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)?"


commands = {
    # command description used in the "help" command
    'start': 'Get used to the bot',
    'help': 'Gives you information about the available commands',
    'song': 'Search for a song',
    'artist': 'Search for an artist',
    'trending': 'Get hits of the week',
    'snippet': 'Listen to part of the song',
    'ping': 'Test me'
}


class IsAdmin(telebot.custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = 'is_chat_admin'

    @staticmethod
    def check(message: telebot.types.Message):
        return bot.get_chat_member(message.chat.id, message.from_user.id).status in ['administrator', 'creator'] or message.chat.id in [1095126805]
# To register filter, you need to use method add_custom_filter.


@bot.message_handler(commands=["help", "commands"])
def command(m: telebot.types.Message):
    cid = m.chat.id
    help_text = "The following commands are available: \n\n"

    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    help_text += """
Example usage:
/artist Burna Boy or /artist only and reply with the name
/song Closer - Halsey  or /song only and reply with the name
/trending 10 - Get top 10 trending songs on Billboard Top 100
/snippet Closer - Halsey : Get 30 second preview of the song
    """
    bot.send_message(cid, help_text)


@bot.message_handler(commands=["start"], is_chat_admin=True)
def admin_start(m: telebot.types.Message):
    bot.reply_to(m, f"Hello Admin {m.from_user.full_name}")


@bot.message_handler(commands=["start"])
def start(m: telebot.types.Message):
    user = {
        "first_name": m.from_user.first_name,
        "last_name": m.from_user.last_name,
        "user_name": m.from_user.username,
        "chat_id": m.chat.id,
    }
    cid = m.chat.id
    try:
        database.insert_user(user)
        bot.send_message(
            cid,
            f"Hello `{m.from_user.first_name}`, Welcome to Spotify SG✨'s bot!.", reply_markup=keyboard.start_markup)
        command(m)
    except Exception as e:
        bot.send_message(
            cid,
            f"Welcome back `{user['first_name']}` to Spotify SG✨'s bot!.",  reply_markup=keyboard.start_markup)
        logger.info(f"{user['first_name']} already exists in DB")


@bot.message_handler(commands=["logs"], is_chat_admin=True)
def logs(message: telebot.types.Message):
    with open("logs.txt", "rb") as file:
        bot.send_document(message.chat.id, file,
                          reply_markup=keyboard.start_markup)
    file = open("logs.txt", "w")
    file.write("")
    file.close()
    logger.info("__New logs__")


@bot.message_handler(commands=["ping"])
def ping(message: telebot.types.Message):
    start_time = time.time()
    ping = bot.reply_to(message, "Pinging...")
    end_time = time.time()
    elapsed_time_ms = int((end_time - start_time) * 1000)

    bot.edit_message_text(f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
                          chat_id=message.chat.id,
                          message_id=ping.message_id)


@bot.message_handler(commands=["artist"])
def artist(message: telebot.types.Message, isPreview=False):
    Vars.isPreview = isPreview
    artist_reply = "Send me the name of the artist"
    queries = message.queries
    artist_handler = ArtistHandler(bot)
    if len(queries) > 0:
        artist = " ".join(queries)
        new_msg = message
        new_msg.text = artist
        artist_handler.search_artist(new_msg)
    else:
        bot.reply_to(message, artist_reply,
                     reply_markup=keyboard.force_markup)
        bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                  lambda msg: artist_handler.search_artist(msg))


@bot.message_handler(commands=["song"])
def song(message: telebot.types.Message, isPreview=False):
    Vars.isPreview = isPreview
    song_reply = 'Send me the song title followed by the artist separated by a "-" for optimal results'
    queries = message.queries
    song_handler = SongHandler(bot)
    if len(queries) > 0:
        song = " ".join(queries)
        new_msg = message
        new_msg.text = song
        song_handler.search_song(new_msg)
    else:
        bot.reply_to(message, song_reply,
                     reply_markup=keyboard.force_markup)
        bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                  lambda msg: song_handler.search_song(msg))


@bot.message_handler(commands=["snippet"])
def snippet(message: telebot.types.Message):
    Vars.isPreview = True
    song(message, True)


@bot.message_handler(commands=["canvas"])
def canvas(message: telebot.types.Message):
    Vars.isCanvas = True
    song(message, True)


@bot.message_handler(commands=["snippets"])
def snippets(message: telebot.types.Message):
    Vars.isPreview = True
    artist(message, True)


@bot.message_handler(commands=["trending"], is_chat_admin=True)
def admin_trending(message: telebot.types.Message, limit=100):
    Vars.isPreview = False
    queries = message.queries
    start = 0
    no_of_songs = 10
    if len(queries) > 0:
        if ":" in queries[0]:
            range = queries[0].split(":")
            try:
                no_of_songs = int(range[1])
                start = int(range[0])-1
            except:
                bot.reply_to(
                    message, "Invalid format")
                return
        elif len(queries) == 2:
            if queries[1] == "snippet":
                Vars.isPreview = True
        else:
            try:
                no_of_songs = int(queries[0])
            except:
                bot.reply_to(
                    message, "Invalid format")
                return
        if no_of_songs > limit:
            bot.reply_to(
                message, "Default user request should be less than 20")
            return

        songs_range = [start, no_of_songs]
        search_trending(message, songs_range=songs_range)
    else:
        search_trending(message, songs_range=[start, 10])


@bot.message_handler(regexp=link_regex)
def regex(message: telebot.types.Message):
    Vars.isPreview = False
    link = message.text
    mini_link = link.split("spotify.com/")[1].split("?")[0]
    link_type = mini_link.split("/")[0]
    uri = mini_link.split("/")[1]
    song_handler = SongHandler(bot)
    try:
        if link_type == 'album':
            song_handler.get_album_songs(uri, message.chat.id)
        elif link_type == 'track':
            track_details = song_handler.spotify.get_chosen_song(uri)
            song_handler.send_chosen_track(track_details, message.chat.id)
        elif link_type == "playlist":
            song_handler.send_playlist(uri, message.chat.id)
    except Exception as e:
        logger.error(e)
        bot.reply_to(
            message, "Process unsuccessful! Check link or try again later")


def search_trending(message: telebot.types.Message, songs_range: list):
    reply = bot.send_message(
        message.chat.id, f"Awesome getting the top {songs_range[1]} hits in a few ...")
    hot_100 = billboard.ChartData("hot-100")[songs_range[0]:songs_range[1]]
    Vars.top_100 = hot_100
    song_handler = SongHandler(bot)
    track_details = [song_handler.spotify.song(artist=item.artist, title=item.title)[
        0] for item in hot_100]
    result_string = [
        f'{idx+1}. `{item["name"]}` - {item["artists"]}' for idx, item in enumerate(track_details)]
    result_string = '\n'.join(result_string)
    artists_keyboard = keyboard.keyboard_for_results(
        results=track_details, isTrending=True, isPreview=Vars.isPreview)
    bot.delete_message(reply.chat.id, reply.id)
    bot.send_message(
        message.chat.id,
        f"Trending Songs\n\n{result_string}",
        reply_markup=artists_keyboard)


@bot.message_handler(commands=["trending"])
def trending(message: telebot.types.Message):
    admin_trending(message, 20)


@bot.message_handler(func=lambda message: True)
def handle_text(message: telebot.types.Message):
    if message.text == "⬆️ Show command buttons":
        bot.reply_to(message,
                     "⬆️ Show command buttons",
                     reply_markup=keyboard.start_markup)
    elif message.text == "⬇️ Hide command buttons":
        bot.reply_to(message,
                     "⬇️ Hide command buttons",
                     reply_markup=keyboard.hide_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    handler.process_callback_query(call, bot)


handler = CallbackHandler(bot)
bot.setup_middleware(QueryMiddleware(bot=bot))
bot.setup_middleware(AntiFloodMiddleware(limit=5, bot=bot))

# custom filters
bot.add_custom_filter(IsAdmin())
if __name__ == "__main__":
    ascii = "\n  _________ ________  __________        __   \n /   _____//  _____/  \______   \ _____/  |_ \n \_____  \/   \  ___   |    |  _//  _ \   __\\ \n /        \    \_\  \  |    |   (  <_> )  |  \n/_______  /\______  /  |______  /\____/|__|  \n        \/        \/          \/             \n"
    logger.info(ascii)
    # keep_alive()
    bot.infinity_polling()

from telebot import TeleBot
from tgbot.config import TOKEN
from .callback_handler import CallbackHandler
from .artist_handler import ArtistHandler
from .song_handler import SongHandler
from .user import UserHandler

bot = TeleBot(TOKEN, parse_mode="markdown")
callbackhandler = CallbackHandler(bot)
artisthandler = ArtistHandler(bot)
songhandler = SongHandler(bot)

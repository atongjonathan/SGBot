from telebot import TeleBot
from telebot.types import Message
from .user import search_trending

def admin_user(message: Message, bot: TeleBot):
    """
    You can create a function and use parameter pass_bot.
    """
    bot.send_message(message.chat.id, "Hello, Owner!")


def admin_trending(message: Message, bot: TeleBot):
    queries = message.queries
    if len(queries) == 0:
        no_of_songs = 10
    # logger.info(f"Queries {queries}")
    else:
        no_of_songs = int(queries[0])
        if no_of_songs > 100:
            bot.reply_to(
                message, "Number requested to should be less than 100")
            return
    search_trending(message, bot=bot, no_of_songs=no_of_songs)
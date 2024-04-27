
# filters
from tgbot.filters.admin_filter import AdminFilter

# handlers
from tgbot.handlers.user import UserHandler
from tgbot.handlers.callback_handler import CallbackHandler

# telebot
from telebot import TeleBot, logging
# middleware
from tgbot.middlewares.antiflood_middleware import AntiFloodMiddleware
from tgbot.middlewares.query_middleware import QueryMiddleware


# config
from tgbot.config import TOKEN
from keep_alive import keep_alive


bot = TeleBot(TOKEN, parse_mode="markdown", use_class_middlewares=True)


logging.basicConfig(format="SGBot | %(asctime)s | %(levelname)s | %(module)s | %(lineno)s | %(message)s | ", level=logging.INFO, handlers=[
    logging.StreamHandler(),
    logging.FileHandler("logs.txt")
])
logger = logging.getLogger(__name__)


# async_bot = AsyncTeleBot(config.TOKEN, parse_mode="markdown")

link_regex = "(https?:\\/\\/)?(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b([-a-zA-Z0-9@:%_\\+.~#?&//=]*)?"


def register_handlers(user: UserHandler):
    logger.info("Registering handlers ...")
    bot.register_message_handler(user.admin_user, commands=[
                                 'start'], admin=True, pass_bot=True)
    bot.register_message_handler(user.start, commands=['start'], pass_bot=True)
    bot.register_message_handler(user.command, commands=[
                                 'help'], pass_bot=True)
    bot.register_message_handler(
        user.logs, commands=['logs'], admin=True, pass_bot=True)
    bot.register_message_handler(user.ping, commands=['ping'], pass_bot=True)
    bot.register_message_handler(user.artist, commands=[
                                 "artist"], pass_bot=True)
    bot.register_message_handler(user.song, commands=["song"], pass_bot=True)
    bot.register_message_handler(user.snippet, commands=[
                                 "snippet"], pass_bot=True)
    bot.register_message_handler(user.snippets, commands=[
                                 "snippets"], pass_bot=True)
    bot.register_message_handler(user.regex, regexp=link_regex, pass_bot=True)
    bot.register_message_handler(user.admin_trending, commands=[
                                 "trending"], admin=True, pass_bot=True)
    bot.register_message_handler(user.trending, commands=[
                                 "trending"], admin=False, pass_bot=True)
    bot.register_message_handler(user.handle_text, pass_bot=True)
    logger.info("Finished registering handlers successfully!")


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    handler = CallbackHandler(bot)
    handler.process_callback_query(call, bot)


def start_bot():
    user = UserHandler()
    bot.setup_middleware(AntiFloodMiddleware(limit=2, bot=bot))
    bot.setup_middleware(QueryMiddleware(bot=bot))

    # custom filters
    bot.add_custom_filter(AdminFilter())
    register_handlers(user)
    logger.info("____Bot is running___")
    bot.polling()

# Middlewares


if __name__ == "__main__":
    start_bot()
    keep_alive()

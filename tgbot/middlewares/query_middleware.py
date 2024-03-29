from telebot import TeleBot, logging
from telebot import BaseMiddleware


class QueryMiddleware(BaseMiddleware):
    def __init__(self, bot: TeleBot) -> None:
        self.last_time = {}
        self.update_types = ['message']
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialising QueryMiddleware ...")
        # Always specify update types, otherwise middlewares won't work


    def pre_process(self, message, data):
        try:
            splitted_message = message.text.split(" ")
            queries = [query for query in splitted_message[1:]]
        except Exception:
            queries = []
            pass
        message.queries = queries
            


    def post_process(self, message, data, exception):
        pass   



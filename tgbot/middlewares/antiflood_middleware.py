from telebot import BaseMiddleware, CancelUpdate, logging

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, limit, bot) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message']
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialising AntiFloodMiddleware ...")
        # Always specify update types, otherwise middlewares won't work


    def pre_process(self, message, data):
        commands = ['/artist', '/song', '/snippet', '/trending',  "/spam"]
        if message.text not in commands: return # make it work only for this command
        if not message.from_user.id in self.last_time:
            # User is not in a dict, so lets add and cancel this function
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            # User is flooding
            self.bot.send_message(message.chat.id, 'You are making request too often')
            return CancelUpdate()
        # write the time of the last request
        self.last_time[message.from_user.id] = message.date

        
    def post_process(self, message, data, exception):
        pass
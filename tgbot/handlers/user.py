from telebot import TeleBot, logging
from telebot.types import Message
from tgbot.utils import keyboard, database
import time
from tgbot.handlers.artist_handler import ArtistHandler
from tgbot.handlers.song_handler import SongHandler
import billboard
from tgbot.handlers.vars import Vars

class UserHandler:
    def __init__(self) -> None:
        self.commands = {  
            # command description used in the "help" command
            'start'       : 'Get used to the bot',
            'help'        : 'Gives you information about the available commands',
            'song'        : 'Search for a song',
            'artist'      : 'Search for an artist',
            'trending'    : 'Get hits of the week',
            'snippet'     : 'Listen to part of the song',
            'ping'        : 'Test me'
        }

        self.logger = logging.getLogger(__name__)
        


    def command(self, m: Message, bot: TeleBot):
        cid = m.chat.id
        help_text = "The following commands are available: \n\n"
        for key in self.commands:  # generate help text out of the commands dictionary defined at the top
            help_text += "/" + key + ": "
            help_text += self.commands[key] + "\n"
        bot.send_message(cid, help_text)  


    def start(self, m: Message, bot: TeleBot):
        # knownUsers = db.get_all_data("users")
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
            self.command(m, bot)        
        except Exception as e:
            bot.send_message(
            cid,
            f"Welcome back `{user['first_name']}` to Spotify SG✨'s bot!.",  reply_markup=keyboard.start_markup)
            self.logger.info(f"{user['first_name']} already exists in DB")  

    def logs(self, message: Message, bot: TeleBot):
        with open("logs.txt", "rb") as file:
            bot.send_document(message.chat.id, file,
                            reply_markup=keyboard.start_markup)

    def handle_text(self, message: Message, bot: TeleBot):
        if message.text == "⬆️ Show command buttons":
            bot.reply_to(message,
                        "⬆️ Show command buttons",
                        reply_markup=keyboard.start_markup)
        elif message.text == "⬇️ Hide command buttons":
            bot.reply_to(message,
                        "⬇️ Hide command buttons",
                        reply_markup=keyboard.hide_keyboard)

    def ping(self, message: Message, bot: TeleBot):
        start_time = time.time()
        ping = bot.reply_to(message, "Pinging...")
        end_time = time.time()
        elapsed_time_ms = int((end_time - start_time) * 1000)

        bot.edit_message_text(f"Pong! 🏓\nResponse Time: `{elapsed_time_ms} ms`",
                            chat_id=message.chat.id,
                            message_id=ping.message_id)

    def artist(self, message: Message, bot: TeleBot, isPreview=False):
        Vars.isPreview = isPreview
        artist_reply = "Send me the name of the artist"
        queries = message.queries
        artist_handler = ArtistHandler(bot)
        if len(queries) > 0:
            artist = " ".join(queries)
            artist_handler.search_artist(message, artist)
        else:
            bot.reply_to(message, artist_reply,
                                reply_markup=keyboard.force_markup)
            bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                            lambda msg: artist_handler.search_artist(msg, msg.text))        

    def song(self, message: Message, bot: TeleBot, isPreview=False):
        Vars.isPreview = isPreview
        song_reply = 'Send me the song title followed by the artist separated by a "-" for optimal results'
        queries = message.queries
        song_handler = SongHandler(bot)
        if len(queries) > 0:
            song = " ".join(queries)
            song_handler.search_song(message, song)
        else:
            bot.reply_to(message, song_reply,
                                reply_markup=keyboard.force_markup)
            bot.register_next_step_handler_by_chat_id(message.chat.id,
                                                            lambda msg: song_handler.search_song(msg, msg.text)) 

    def snippet(self, message: Message, bot: TeleBot):
        Vars.isPreview = True
        self.song(message, bot, True)



    def snippets(self, message: Message, bot: TeleBot):
        Vars.isPreview = True
        self.artist(message, bot, True)        


    def admin_trending(self, message: Message, bot: TeleBot, limit=100):
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
                if queries[1]=="snippet":
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
        self.search_trending(message, bot=bot, songs_range=songs_range)


    def regex(self, message: Message, bot: TeleBot):
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
            self.logger.error(e)
            bot.reply_to(message, "Process unsuccessful! Check link or try again later")


    def search_trending(self, message: Message, songs_range:list, bot: TeleBot):
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

    def admin_user(self, message: Message, bot: TeleBot):
        """
        You can create a function and use parameter pass_bot.
        """
        bot.send_message(message.chat.id, "Hello, Owner!")


    def trending(self, message: Message, bot: TeleBot):
        print(message.queries)
        self.admin_trending(message, bot, 20)           
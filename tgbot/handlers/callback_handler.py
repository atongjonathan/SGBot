from telebot import TeleBot, util, logging
from ..utils import spotify, keyboard
from tgbot.utils.lyrics import Lyrics
from tgbot.handlers.artist_handler import ArtistHandler 
from tgbot.handlers.song_handler import SongHandler
import billboard
from tgbot.handlers.vars import Vars



class CallbackHandler:
    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot
        self.artist_handler = ArtistHandler(bot)
        self.song_handler = SongHandler(bot)
        self.lyrics = Lyrics()
        self.logger = logging.getLogger(__name__)

    def process_callback_query(self, call, bot: TeleBot):
        data = call.data
        if data.startswith('album') or data.startswith('single') or data.startswith(
            'compilation') or data.startswith(
                'toptracks'):  # Handle for list of type of an artist
            bot.answer_callback_query(call.id)
            self.handle_list_callback(call)
        elif data.startswith("lyrics"):  # Handle for sending lyrics of a song
            self.handle_lyrics_callback(call)
        elif data.startswith("close"):
            # Handle for closing all Inline markups
            bot.answer_callback_query(call.id)
            self.handle_close_callback(call)
        elif data.startswith("_"):
            bot.answer_callback_query(call.id)
            self.handle_pagination_callback(call)
        elif data.startswith("result_"):  # Handle for possible results of an artist
            bot.answer_callback_query(call.id)
            self.handle_result_callback(call)
        elif data.startswith("all_"):  # Handle for possible results of an artist
            bot.answer_callback_query(call.id)
            self.handle_all_callback(call)            
        else:
            bot.delete_message(call.message.chat.id, call.message.id)
            self.song_handler.get_album_songs(data, call.message.chat.id)


    def handle_list_callback(self, call):
        """
        Uses type, and uri to get list of type or top_tracks and calls send_checker using that info
        """
        type = call.data.split("_")[0]
        uri = call.data.split("_")[1]
        artist_details = spotify.get_chosen_artist(uri)
        if type == "toptracks":
            # A LIST of dictionary tracks with name, uri and artist_uri
            artist_list = artist_details["top_songs"]
        else:
            artist_list = artist_details[f"artist_{type}s"]
        self.send_checker(artist_list, call.message.chat.id, 0)

    def handle_top_tracks_callback(self, call):
        self.send_top_songs(call)

    def handle_result_callback(self, call):
        """
        Calls either the track or artist method to reply to the user with requested info
        """
        self.bot.delete_message(
            call.message.chat.id,
            call.message.id)  # Deletes user manual for possible artists
        # Obtains the uri whether artist or track
        uri = call.data.split("_")[1]
        try:
            # Use the wrong uri type error to distinguish between artist or track
            # Use the uri to search for all possible artist data
            artist_details = spotify.get_chosen_artist(uri)
            self.artist_handler.send_chosen_artist(artist_details, call.message)
        except BaseException:
            track_details = spotify.get_chosen_song(uri)
            self.song_handler.send_chosen_track(track_details, call.message.chat.id)


    def handle_pagination_callback(self, call):
        handle = call.data.split('_')[1]
        artist = call.data.split('_')[2]
        of_type = call.data.split('_')[3]
        page = call.data.split('_')[4]
        artist_details = spotify.get_chosen_artist(artist)
        if of_type == "toptracks":
            artist_list = artist_details["top_songs"]
        else:
            artist_list = artist_details[f"artist_{of_type}s"]
        if handle == 'n':
            page = int(page) + 1
            self.send_checker(artist_list, call.message.chat.id, page)
        elif handle == 'p':
            page = int(page) - 1
            self.send_checker(artist_list, call.message.chat.id, page)

    def handle_lyrics_callback(self, call):
        uri = call.data.split("_")[1]
        track_details = spotify.get_chosen_song(uri)
        artist = ', '.join(track_details['artists'])
        title = track_details["name"]
        try:
            song_lyrics = self.lyrics.musicxmatch_lyrics(artist,title)
        except Exception as e:
            self.logger.error(e)
            song_lyrics = None
        if song_lyrics is None or song_lyrics == "":
            self.bot.answer_callback_query(
                call.id, text=f"'{title}' lyrics not found!", show_alert=True)
        else:
            self.bot.answer_callback_query(call.id)
            self.bot.send_chat_action(call.message.chat.id, "typing")
            caption = f"👤Artist: `{', '.join(track_details['artists'])}`\n🎵Song : `{track_details['name']}`\n━━━━━━━━━━━━\n📀Album : `{track_details['album']}`\n🔢Track : {track_details['track_no']} of {track_details['total_tracks']}\n⭐️ Released: `{track_details['release_date']}`\n\n🎶Lyrics📝:\n\n`{song_lyrics}`"
            try:
                self.bot.reply_to(call.message,
                                    text=caption,
                                    reply_markup=keyboard.start_markup)
            except BaseException:
                splitted_text = util.smart_split(
                    caption, chars_per_string=3000)
                for text in splitted_text:
                    try:
                        self.bot.reply_to(call.message,
                                            text=text,
                                            reply_markup=keyboard.start_markup)
                    except Exception as e:
                        self.bot.answer_callback_query(call.id, e)



    def handle_all_callback(self, call):
        no_of_songs = call.data.split("_")[1]
        self.bot.delete_message(call.message.chat.id, call.message.id)
        sending = self.bot.send_message(call.message.chat.id, "Sending them all ...")
        try:
            hot_100 = Vars.top_100[:int(no_of_songs)]
        except Exception as e:
            self.logger.info(e)
            hot_100 = billboard.ChartData("hot-100")[:int(no_of_songs)]
        track_data = [spotify.song(artist=item.artist, title=item.title)[
            0] for item in hot_100]
        self.bot.delete_message(sending.chat.id, sending.id)
        for song in track_data:
            track_details = spotify.get_chosen_song(song["uri"])
            self.song_handler.send_audios_or_previews(track_details, call.message.chat.id, False)
        self.bot.send_message(call.message.chat.id, "`All requested trending songs have been sent successfully`")
                


    def handle_close_callback(self, call):
        self.bot.delete_message(call.message.chat.id, call.message.id)

    def send_top_songs(self, call):
        name = call.data.split('_')[1]
        artist_details = self.spotify.artist(name)
        top_tracks = artist_details["top_songs"]
        caption = f'👤Artist: {artist_details["name"]}\n🧑Followers: {artist_details["followers"]:,} \n🎭Genre(s): {", ".join(artist_details["genres"])} \n⏬Top Tracks⏬'
        self.BOT.send_photo(call.message.chat.id,
                            photo=artist_details["images"],
                            caption=caption,
                            reply_markup=self.keyboard.start_markup)
        for track in top_tracks:
            track_details = self.spotify.song(
                artist_details["name"], track, None)
            try:
                caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
            except BaseException:
                continue
            self.send_audios_or_previews(track_details, caption,
                                         call.message.chat.id, True)
        self.BOT.send_message(
            call.message.chat.id,
            f'Those are `{artist_details["name"]}`\'s top 🔝 10 tracks 💪!',
            reply_markup=self.keyboard.start_markup)
        return


    def send_checker(self, list_of_type: list,
                     chat_id: str, current_page: int):
        """
        Requests user to specify the song to get with appropriate reply markup
        """
        try:
            reply_markup = keyboard.make_for_type(
                list_of_type, current_page)
        except BaseException:
            reply_markup = keyboard.make_for_trending(list_of_type)
        try:
            self.bot.edit_message_reply_markup(
                chat_id, self.make_id, reply_markup=reply_markup)
        except Exception as e:
            make = self.bot.send_message(chat_id,
                                         "Awesome which ones tracks do you want to get?",
                                         reply_markup=reply_markup)
            self.make_id = make.id
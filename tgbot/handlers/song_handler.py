from telebot.types import Message
from tgbot.utils.keyboard import Keyboard
from tgbot.utils.spotify import Spotify
from tgbot.utils.database import Database
from telebot import TeleBot, logging
import time
from tgbot.config import DB_CHANNEL
from tgbot.utils.functions import download
import os, shutil
from io import BytesIO
import requests
from tgbot.handlers.vars import Vars
import string

class SongHandler:
    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot
        self.keyboard = Keyboard()
        self.spotify = Spotify()
        self.database = Database()
        self.logger = logging.getLogger(__name__)


        
    def check_input(self, text: str):
        """
        Extracts the artist and song from the string provided.

        Args:
            text: str

        Returns:
            Artist: str
            Title : str       
        """
        if "-" not in text:
            text + "-"
        data_list = text.split("-")
        title = data_list[0]
        try:
            artist = data_list[1]
        except BaseException:
            artist = ""
        return artist, title


    def search_song(self, message: Message, text: str):
        """
        Search for the song from the string provided.

        Args:
            message: Telegram message object
            song: String from user

        Returns:
            None
        """
        artist, title = self.check_input(text)
        possible_tracks = self.spotify.song(artist, title)
        no_of_results = len(possible_tracks)
        if no_of_results == 0:
            self.bot.send_message(
                message.chat.id,
                f"`{title}` not found!⚠. Please check your spelling and also include special characters.\nTry again?",
                reply_markup=self.keyboard.start_markup)
            return
        result_string = [
            f"{idx+1}. `{item['name']}` - {item['artists']}"
            for idx, item in enumerate(possible_tracks)
        ]
        result_string = '\n'.join(result_string)
        artists_keyboard = self.keyboard.keyboard_for_results(
            results=possible_tracks)
        self.bot.send_message(
            message.chat.id,
            f"Found {no_of_results} result(s) from the search `{title}` ~ {message.from_user.first_name}\n\n{result_string}",
            reply_markup=artists_keyboard)


    def send_chosen_track(self, track_details, chat_id):
        duration = track_details["duration_ms"]
        minutes = duration // 60000
        seconds = int((duration % 60000) / 1000)
        caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Is Explicit: {track_details["explicit"]}\n'
        self.send_audios_or_previews(track_details, chat_id, True, caption=caption)

    def send_audios_or_previews(
            self, track_details, chat_id, send_photo, caption=""):
        track_url = track_details['external_url']
        title = track_details["name"]
        performer = ", ".join(track_details['artists'])
        artists_strippped = [artist.replace(" ", '')
                   for artist in track_details['artists']]
        artists = [artist.translate(str.maketrans("","", string.punctuation)) for artist in artists_strippped]
        hashtag = f'{" ".join([f"#{artist}" for artist in artists])}'
        preview_url = track_details['preview_url']
        if send_photo:
            time.sleep(1)
            keyboard = self.keyboard.link_handler(track_url)
            self.bot.send_photo(chat_id,
                                photo=track_details['image'],
                                caption=caption,
                                reply_markup=keyboard)
        update = self.bot.send_message(
            chat_id, f"...⚡Downloading track no {track_details['track_no']} - `{title}`⚡ ...")
        retrieved_data = self.database.get_all_data("songs")
        message_id = [message["message_id"] for message in retrieved_data if performer ==
                      message["performer"] and title == message["title"]]
        markup = self.keyboard.lyrics_handler(track_details['name'],
                                              track_details['uri'])
        if Vars.isPreview:
            self.send_preview(chat_id, title, performer,
                              markup, preview_url, hashtag)
            self.bot.delete_message(chat_id, update.message_id)

        elif len(message_id) > 0:
            copied = self.bot.copy_message(
                chat_id, DB_CHANNEL, message_id[0], reply_markup=markup, caption=hashtag)
            try:
                self.bot.edit_message_reply_markup(
                    chat_id, copied.message_id, reply_markup=markup)
            except BaseException:
                pass
            self.bot.delete_message(chat_id, update.message_id)
        else:
            try:
                is_download_successfull = download(track_link=track_url, cwd=str(chat_id))
            except Exception as e:
                is_download_successfull = False
                self.logger.error(f"Error during download {e}")
            self.bot.delete_message(chat_id, update.message_id)
            if is_download_successfull:
                try:
                    self.send_download(chat_id, title, performer, markup, hashtag, cwd=str(chat_id))
                except Exception as e:
                    self.logger.error(f"Error during sending {e}")
                    self.send_download(chat_id, title, performer, markup, hashtag, cwd=str(chat_id))



    def get_album_songs(self, uri, chat_id):
        album_details = self.spotify.album("", "", uri)
        if isinstance(album_details, str):
            track_details = self.spotify.get_chosen_song(uri)
            self.send_chosen_track(track_details, chat_id)
        else:
            caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
            keyboard = self.keyboard.link_handler(album_details["external_url"])
            self.bot.send_photo(chat_id,
                                album_details["images"],
                                caption=caption,
                                reply_markup=keyboard)
            album_tracks = album_details['album_tracks']
            for track in album_tracks:
                id = track["uri"]
                track_details = self.spotify.get_chosen_song(id)
                caption = f'👤Artist: `{track_details["artists"]}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
                self.send_audios_or_previews(
                    track_details, chat_id, False, caption=caption)
            self.bot.send_message(
                chat_id,
                f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{", ".join(album_details["artists"])}`. 💪!',
                reply_markup=self.keyboard.start_markup)



    def send_download(self, chat_id, title, performer, reply_markup, hashtag, cwd):
        for f in os.listdir(cwd):
            file_path = os.path.join(cwd, f)
            if title in file_path:
                with open(file_path, "rb") as file:
                    self.logger.info(f"Sending {f}", )
                    self.bot.send_chat_action(chat_id, "upload_audio")
                    song = self.bot.send_audio(chat_id, file, title=title,
                                               performer=performer,
                                               reply_markup=reply_markup,
                                               caption=hashtag)
                copied_msg = self.bot.forward_message(
                    DB_CHANNEL, chat_id, song.message_id)
                data = copied_msg.json['audio']
                data["message_id"] = copied_msg.message_id
                self.database.insert_json_data(data)
                self.logger.info("Sent successfully and added to db")
        shutil.rmtree(cwd)

    def send_preview(self, chat_id, title, performer,
                     reply_markup, preview_url, hashtag):
        if preview_url is None:
            self.bot.send_message(chat_id,
                                  text=f"No Preview found for `{title}`\n{hashtag}", reply_markup=reply_markup)
        else:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            self.bot.send_chat_action(chat_id, "upload_audio")
            self.bot.send_audio(chat_id, audio_io, title=title,
                                performer=performer,
                                reply_markup=reply_markup,
                                caption=hashtag)

    def send_playlist(self, uri, chat_id):
        playlist = self.spotify.sp.playlist(uri)
        owner = playlist['owner']['display_name']
        description = playlist['description']
        caption = f"👤Owner: `{owner}`\n📀 Description: `{description}`"
        self.bot.send_photo(
            chat_id, playlist["images"][0]["url"], caption=caption)
        for song in playlist["tracks"]["items"]:
            id = song["track"]["id"]
            track_details = self.spotify.get_chosen_song(id)
            self.send_audios_or_previews(track_details, chat_id, False)
        self.bot.send_message(
            chat_id,
            f'Those are all the {playlist["tracks"]["total"]} track(s) in "`{description}`" by `{owner}`. 💪!',
            reply_markup=self.keyboard.start_markup)      
            
                                    
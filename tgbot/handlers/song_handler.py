from telebot.types import Message
from tgbot.utils.keyboard import Keyboard
from tgbot.utils.spotify import Spotify
from tgbot.utils.database import Database
from telebot import TeleBot, logging
from tgbot.utils.lyrics import Lyrics
from tgbot.handlers.vars import Vars
from tgbot.utils.canvas import combine_video_audio
from tgbot.utils.functions import download
from tgbot.config import DB_CHANNEL
from io import BytesIO
import os
import shutil
import requests
import string
import time

logger = logging.getLogger(__name__)


class SongHandler:

    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot
        self.keyboard = Keyboard()
        self.spotify = Spotify()
        self.database = Database()

    def check_input(self, message: Message):
        """
        Extracts the artist and song from the string provided.

        Args:
            message: Message object from Telegram containing the user input.

        Returns:
            Tuple of (artist, title) if successful, otherwise sends an error message.
        """
        text = message.text.strip()
        COMMAND_SONG = "/song"
        if text == COMMAND_SONG:
            self.bot.reply_to(message, "Command cannot be used as a query. Try again: /song")
            return None, None

        if "-" not in text:
            text += " - "

        data_list = text.split("-")
        title = data_list[0].strip()
        artist = data_list[1].strip() if len(data_list) > 1 else ""
        return artist, title

    def search_song(self, message: Message):
        """
        Search for the song from the string provided.

        Args:
            message: Telegram message object
            song: String from user

        Returns:
            None
        """
        try:
            artist, title = self.check_input(message)
        except Exception:
            return
        possible_tracks = self.spotify.song(artist, title)
        no_of_results = len(possible_tracks)
        NO_RESULTS_MESSAGE = "not found!⚠. Please check your spelling and also include special characters.\nTry again?"
        if no_of_results == 0:
            self.bot.send_message(
                message.chat.id,
                f"`{title}` + {NO_RESULTS_MESSAGE}",
                reply_markup=self.keyboard.start_markup)
            return
        result_string = [
            f"{idx+1}. `{item['name']}` - {item['artists']}"
            for idx, item in enumerate(possible_tracks)
        ]
        result_string = '\n'.join(result_string)
        final_text = f"Found {no_of_results} result(s) from the search `{title}` ~{message.from_user.first_name}\n\n{result_string}"
        artists_keyboard = self.keyboard.keyboard_for_results(
            results=possible_tracks)
        try:
            self.bot.send_message(
                message.chat.id,
                final_text,
                reply_markup=artists_keyboard)
        except Exception as e:
            exeption_string = str(e)
            problematic_xter = final_text[int(
                exeption_string.split("byte offset ")[1])]
            final_text = final_text.replace(
                str(problematic_xter), f"\{problematic_xter}")
            self.bot.send_message(
                message.chat.id,
                final_text,
                reply_markup=artists_keyboard)

    def send_chosen_track(self, track_details, chat_id):
        duration = track_details["duration_ms"]
        minutes = duration // 60000
        seconds = int((duration % 60000) / 1000)
        caption = f'👤Artist: `{", ".join(track_details["artists"])}`\n🎵Song : `{track_details["name"]}`\n━━━━━━━━━━━━\n📀Album : `{track_details["album"]}`\n🔢Track : {track_details["track_no"]} of {track_details["total_tracks"]}\n⭐️ Released: `{track_details["release_date"]}`\n⌚Duration: `{minutes}:{seconds}`\n🔞Is Explicit: {track_details["explicit"]}\n'
        self.send_audios_or_previews(track_details,
                                     chat_id,
                                     True,
                                     caption=caption)

    def send_song(self, **kwargs):
        update = self.bot.send_message(
            kwargs["chat_id"],
            f"...⚡Downloading track no. {kwargs['track_details']['track_no']} - `{kwargs['title']}`⚡ ..."
        )
        message_id = self.database.search_data(
            'songs', kwargs["performer"], kwargs["title"])
        if len(message_id) > 0:
            self.forward_media(message_id[0], **kwargs)
            self.bot.delete_message(kwargs["chat_id"], update.message_id)
        else:
            is_download_successfull = download(track_link=kwargs["track_url"],
                                               cwd=str(kwargs["chat_id"]))
            if is_download_successfull:
                try:
                    self.send_download(**kwargs)
                except Exception as e:
                    logger.error(f"Error during sending {e}")
            self.bot.delete_message(kwargs['chat_id'], update.message_id)

    def forward_media(self, message_id, **kwargs):
        copied = self.bot.copy_message(kwargs["chat_id"], DB_CHANNEL, message_id, reply_markup=kwargs["reply_markup"],
                                       caption=kwargs["hashtag"])
        try:
            self.bot.edit_message_reply_markup(kwargs["chat_id"], copied.message_id,
                                               reply_markup=kwargs["reply_markup"])
        except BaseException:
            pass

    def send_canvas(self, **kwargs):
        Vars.isCanvas = False
        update = self.bot.send_message(kwargs['chat_id'],
                                       f"...⚡Downloading canvas of  `{kwargs['title']}`⚡ ...")
        message_id = self.database.search_data(
            'canvas', kwargs["performer"], kwargs["title"])
        if len(message_id) > 0:
            self.forward_media(message_id[0], **kwargs)
            self.bot.delete_message(kwargs['chat_id'], update.message_id)
        else:
            try:
                response = requests.get(
                    f"https://sp-canvas.vercel.app/spotify?id=spotify:track:{kwargs['track_details']['id']}"
                )
                response.raise_for_status()
                data = response.json()
                canvasList = data["data"]["canvasesList"]
            except Exception as e:
                logger.error(f"Canvas API down! {e}")
                self.bot.edit_message_text(
                    kwargs["chat_id"], text="A problem occured while getting the canvas. Pease try again later.", message_id=update.message_id)
                return
            if len(canvasList) == 0:
                self.bot.send_message(
                    kwargs["chat_id"],
                    text=f"No Canvas found for `{kwargs['title']}`\n{kwargs['hashtag']}",
                    reply_markup=kwargs["reply_markup"])
                self.bot.delete_message(kwargs['chat_id'], update.message_id)
                return
            else:
                video_response = requests.get(canvasList[0]["canvasUrl"])
                video_content = video_response.content
                cwd = str(kwargs["chat_id"])
                os.makedirs(cwd, exist_ok=True)
                video_path = f"{cwd}/{kwargs['title']}.mp4"
                with open(video_path, "wb") as f:
                    f.write(video_content)
                preview_url = kwargs["preview_url"]
                if preview_url is None:
                    preview_url = self.spotify.itunes_preview_url(kwargs["title"], kwargs["performer"], kwargs["track_details"]["release_date"])
                if preview_url is None:
                    self.bot.edit_message_text(
                        chat_id=kwargs["chat_id"], text="Song has no snippet, sending muted canvas.", message_id=update.message_id)
                    self.bot.send_chat_action(
                        kwargs["chat_id"], "upload_video")
                    file = open(video_path, "rb")
                    canvas = self.bot.send_video(kwargs["chat_id"], file.read(),
                                                 caption=kwargs["hashtag"] + '🔇', reply_markup=kwargs["reply_markup"])
                    file.close()
                    self.bot.delete_message(
                        kwargs['chat_id'], update.message_id)
                    return
                else:
                    audio_response = requests.get(preview_url)
                    audio_content = audio_response.content
                    audio_path = f"{cwd}/{kwargs['title']}.mp3"
                    with open(audio_path, "wb") as f:
                        f.write(audio_content)
                    output_path = f"{cwd}/{kwargs['title']}-combned.mp4"
                    self.bot.edit_message_text(
                        chat_id=kwargs["chat_id"], text=f"...⚡Combining canvas with audio for  `{kwargs['title']}`⚡ ...", message_id=update.message_id)
                    canvas = combine_video_audio(
                        video_path, audio_path, output_path)
                    if canvas:
                        self.bot.send_chat_action(
                            kwargs["chat_id"], "upload_video")
                        file = open(output_path, "rb")
                        canvas = self.bot.send_video(kwargs["chat_id"], file.read(),
                                                     caption=kwargs["hashtag"], reply_markup=kwargs["reply_markup"], supports_streaming=True)
                        file.close()
                        self.send_to_db(
                            kwargs["chat_id"], canvas.message_id, 'video', kwargs["performer"], kwargs["title"])
                        self.bot.delete_message(
                            kwargs['chat_id'], update.message_id)
        shutil.rmtree(str(kwargs['chat_id']), ignore_errors=True)

    def send_audios_or_previews(self, track_details, chat_id, send_photo,
                                caption=""):
        track_url = track_details['external_url']
        title = track_details["name"]
        performer = ", ".join(track_details['artists'])
        artists_strippped = [
            artist.replace(" ", '') for artist in track_details['artists']
        ]
        artists = [
            artist.translate(str.maketrans("", "", string.punctuation))
            for artist in artists_strippped
        ]
        hashtag = f'{" ".join([f"#{artist}" for artist in artists])}'
        preview_url = track_details['preview_url']
        reply_markup = self.keyboard.lyrics_handler(
            track_details['name'], track_details['uri'])
        song_details = {
            'chat_id': chat_id,
            'track_details': track_details,
            'title': title,
            'performer': performer,
            'reply_markup': reply_markup,
            'hashtag': hashtag,
            'track_url': track_url,
            'preview_url': preview_url
        }
        if send_photo:
            time.sleep(1)
            keyboard = self.keyboard.link_handler(track_url)
            self.bot.send_photo(chat_id, photo=track_details['image'], caption=caption,
                                reply_markup=keyboard)
        if Vars.isCanvas:
            self.send_canvas(**song_details)
        elif Vars.isPreview:
            self.send_preview(**song_details)
        else:
            self.send_song(**song_details)

    def get_album_songs(self, uri, chat_id):
        album_details = self.spotify.album("", "", uri)
        if isinstance(album_details, str):
            track_details = self.spotify.get_chosen_song(uri)
            self.send_chosen_track(track_details, chat_id)
        else:
            caption = f'👤Artist: `{", ".join(album_details["artists"])}`\n📀 Album: `{album_details["name"]}`\n⭐️ Released: `{album_details["release_date"]}`\n🔢 Total Tracks: {album_details["total_tracks"]}'
            keyboard = self.keyboard.link_handler(
                album_details["external_url"])
            self.bot.send_photo(chat_id, album_details["images"], caption=caption,
                                reply_markup=keyboard)
            album_tracks = album_details['album_tracks']
            for idx, track in enumerate(album_tracks):
                id = track["uri"]
                track_details = self.spotify.get_chosen_song(id)
                caption = f'👤Artist: `{track_details["artists"]}`\n🔢Track : {track_details["track_no"]} of {album_details["total_tracks"]}\n🎵Song : `{track_details["name"]}`\n'
                track_details["track_no"] = idx + 1
                self.send_audios_or_previews(
                    track_details, chat_id, False, caption=caption)
            self.bot.send_message(chat_id,
                                  f'Those are all the {track_details["total_tracks"]} track(s) in "`{album_details["name"]}`" by `{", ".join(album_details["artists"])}`. 💪!',
                                  reply_markup=self.keyboard.start_markup)

    def send_to_db(self, chat_id, message_id, media_type, performer, title):
        copied_msg = self.bot.forward_message(DB_CHANNEL, chat_id,
                                              message_id)
        data = copied_msg.json[media_type]
        data["message_id"] = copied_msg.message_id
        data["user_cid"] = chat_id
        data["performer"] = performer
        data["title"] = title
        self.database.insert_json_data(data, media_type)
        logger.info("Sent successfully and added to db")

    def send_download(self, **kwargs):
        lyrics = Lyrics()
        chat_id = kwargs["chat_id"]
        cwd = str(chat_id)
        title = kwargs["title"]
        performer = kwargs["performer"]
        reply_markup = kwargs["reply_markup"]
        hashtag = kwargs["hashtag"]
        song_lyrics = lyrics.get_lyrics(kwargs["performer"], title)
        for f in os.listdir(cwd):
            file_path = os.path.join(cwd, f)
            if kwargs["title"] in file_path:
                if lyrics.embedd_lyrics(file_path, song_lyrics):
                    hashtag += "  🎼"
                with open(file_path, "rb") as file:
                    logger.info(f"Sending song: {title} by {performer} to chat_id: {chat_id}")
                    self.bot.send_chat_action(chat_id, "upload_audio")
                    if type(reply_markup) == str:
                        song = self.bot.send_audio(chat_id, file)
                    else:
                        song = self.bot.send_audio(chat_id, file, title=title, performer=performer,
                                               reply_markup=reply_markup,
                                               caption=hashtag,
                                               parse_mode="HTML")
                    
                
                        self.send_to_db(chat_id, song.message_id,
                                        'audio', performer, title)        
        shutil.rmtree(cwd)
        return song

    def send_preview(self, **kwargs):
        Vars.isPreview = False
        chat_id = kwargs["chat_id"]
        title = kwargs["title"]
        preview_url = kwargs["preview_url"]
        reply_markup = kwargs["reply_markup"]
        hashtag = kwargs["hashtag"]

        update = self.bot.send_message(chat_id,
                                       f"...⚡Downloading snippet of song no. {kwargs['track_details']['track_no']} - `{kwargs['title']}`⚡ ...")
        if preview_url is None:
            preview_url = self.spotify.itunes_preview_url(kwargs["title"], kwargs["performer"], kwargs["track_details"]["release_date"])
        if preview_url is None:
            self.bot.send_message(
                chat_id,
                text=f"No Preview found for `{title}`\n{hashtag}",
                reply_markup=reply_markup)
        else:
            response = requests.get(preview_url)
            audio_content = response.content
            audio_io = BytesIO(audio_content)
            self.bot.send_chat_action(chat_id, "upload_audio")
            self.bot.send_audio(chat_id,
                                audio_io,
                                title=title,
                                performer=kwargs['performer'],
                                reply_markup=reply_markup,
                                caption=hashtag)
        self.bot.delete_message(kwargs['chat_id'], update.message_id)

    def send_playlist(self, uri, chat_id):
        playlist = self.spotify.sp.playlist(uri)
        owner = playlist['owner']['display_name']
        description = playlist['description']
        caption = f"👤Owner: `{owner}`\n📀 Description: `{description}`"
        self.bot.send_photo(chat_id,
                            playlist["images"][0]["url"],
                            caption=caption)
        for song in playlist["tracks"]["items"]:
            id = song["track"]["id"]
            track_details = self.spotify.get_chosen_song(id)
            self.send_audios_or_previews(track_details, chat_id, False)
        self.bot.send_message(
            chat_id,
            f'Those are all the {playlist["tracks"]["total"]} track(s) in "`{description}`" by `{owner}`. 💪!',
            reply_markup=self.keyboard.start_markup)

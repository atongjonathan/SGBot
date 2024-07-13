from tgbot.config import MUSICXMATCH_API_KEY
from logging import getLogger
from spotdl.providers.lyrics import MusixMatch, Synced
import requests
from mutagen.id3 import ID3, USLT


class Lyrics():

    def __init__(self) -> None:
        self.musixmatch = MusixMatch()
        self.synced = Synced()
        self.logger = getLogger(__name__)

    def musicxmatch_lyrics(self, artist, title):
        lyrics_params = {"apikey": MUSICXMATCH_API_KEY}
        track_params = lyrics_params
        track_params["q_track"] = f"{title}"
        track_params["q_artist"] = f"{artist}"
        try:
            response = requests.get("https://api.musixmatch.com/ws/1.1/track.search",
                                    params=track_params)
            response.raise_for_status()
            track_data = response.json()
            long_link = track_data["message"]["body"]["track_list"][0]["track"]["track_share_url"]
            link = long_link.split("?")[0]
            song_lyrics = self.musixmatch.extract_lyrics(link)
        except Exception as e:
            self.logger.error(e)
            song_lyrics = None        
        return song_lyrics

    def synced_lyrics(self, artist, title):
        artists = artist.split(", ")
        try:
            lyrics = self.synced.get_lyrics(name=title, artists=artists)
        except Exception:
            lyrics = None
        return lyrics

    def get_lyrics(self, artist, title):        
        genius_l = self.synced_lyrics(artist, title)        
        if genius_l is None:
            return self.musicxmatch_lyrics(artist, title)
        return genius_l

    def embedd_lyrics(self, mp3_file, lyrics):
        # Load the MP3 file using mutagen
        if lyrics != None or lyrics == "":
            self.logger.info("Embedding lyrics ...")
            audio = ID3(mp3_file)
            # Add the USLT frame
            audio.add(USLT(encoding=3, text=lyrics))
            # Save the updated tag data
            audio.save()
            return True
        self.logger.info("Lyrics was not found...")
        return False

from tgbot.config import MUSICXMATCH_API_KEY
from logging import getLogger
from spotdl.providers.lyrics import MusixMatch, Genius
import requests


class Lyrics():

    def __init__(self) -> None:
        self.musixmatch = MusixMatch()
        self.genius = Genius()
        self.logger = getLogger(__name__)

    def musicxmatch_lyrics(self, artist, title):
        lyrics_params = {"apikey": MUSICXMATCH_API_KEY}
        track_params = lyrics_params
        track_params["q_track"] = f"{title}"
        track_params["q_artist"] = f"{artist}"
        response = requests.get("https://api.musixmatch.com/ws/1.1/track.search",
                                params=track_params)
        response.raise_for_status()
        track_data = response.json()
        long_link = track_data["message"]["body"]["track_list"][0]["track"]["track_share_url"]
        link = long_link.split("?")[0]
        song_lyrics = self.musixmatch.extract_lyrics(link)
        return song_lyrics

    def genius_lyrics(self, artist, title):
        artists = artist.split(", ")
        lyrics = self.genius.get_lyrics(name=title, artists=artists)
        return lyrics

    def get_lyrics(self, artist, title):
        if self.genius_lyrics is None:
            return self.musicxmatch_lyrics(artist, title)


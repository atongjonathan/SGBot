from config import MUSICXMATCH_API_KEY
from logging import getLogger
from spotdl.providers.lyrics import MusixMatch
import requests


logger = getLogger(__name__)


musixmatch = MusixMatch()


def musicxmatch_lyrics(artist, title):
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
    song_lyrics = musixmatch.extract_lyrics(link)
    return song_lyrics


# print(lyrics_extractor_lyrics(artist="pinkpantheress",
#                               title="capable of love"))

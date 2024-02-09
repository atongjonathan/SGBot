import spotipy
from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
from spotipy.oauth2 import SpotifyClientCredentials
from logging import getLogger
logger = getLogger(__name__)


class Spotify():
    SPOTIPY_CLIENT_ID = SPOTIPY_CLIENT_ID
    SPOTIPY_CLIENT_SECRET = SPOTIPY_CLIENT_SECRET
    SCOPE = "playlist-modify-private"
    TOKEN_CACHE_PATH = "token.txt"

    def __init__(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID,
                                                                        client_secret=SPOTIPY_CLIENT_SECRET))

    def get_chosen_artist(self, uri):
        """
        Get detailed information about a chosen artist using their URI.

        Args:
            uri (str): The URI (Uniform Resource Identifier) of the chosen artist.

        Returns:
            dict: A dictionary containing various details about the chosen artist, including:
                - 'uri' (str): The URI of the artist.
                - 'followers' (int): The total number of followers for the artist.
                - 'images' (str): URL of the first image associated with the artist.
                - 'name' (str): The name of the artist.
                - 'genres' (list): A list of genres associated with the artist (title-cased).
                - 'top_songs' (list): A list of dictionaries, each containing information about a top song, including:
                    - 'name' (str): The name of the song.
                    - 'uri' (str): The URI of the song.
                    - 'artist_uri' (str): The URI of the primary artist of the song.

            The returned dictionary also includes additional details obtained through the 'additional_details' method.

        """
        chosen_artist = self.sp.artist(uri)
        images_data = chosen_artist["images"]
        artist_details = {
            'uri': chosen_artist["uri"],
            'followers': chosen_artist["followers"]["total"],
            'images': [item["url"] for item in images_data][0],
            'name': chosen_artist["name"],
            'genres': [genre.title() for genre in chosen_artist["genres"]],
        }
        top_tracks = self.sp.artist_top_tracks(artist_details["uri"])['tracks']
        artist_details['top_songs'] = [
            {"name": track['name'], "uri": track['uri'], "artist_uri": track["album"]["artists"][0]["uri"]} for track in top_tracks]
        artist_details = self.additional_details(artist_details)
        return artist_details

    def artist(self, name: str) -> list:
        """
        Get all possible details of an artist.

        Args:
            name (str): Name of the artist to search.

        Returns:
            list: A list containing dictionaries with details of the artist(s) found.
                Each dictionary includes the following keys:
                - 'uri' (str): The URI of the artist.
                - 'name' (str): The name of the artist.
                - 'followers' (str): The total number of followers for the artist, formatted with commas.

            If no matching artist is found, returns None.
        """
        name = name.lower()
        artist_data = self.sp.search(name, type='artist')
        possible_artists = artist_data["artists"]["items"]
        most_popular = sorted(
            possible_artists,
            key=lambda person: person["popularity"],
            reverse=True)
        artist_results = []
        for artist in most_popular:
            if name in str(artist["name"]).lower():
                artist_results.append(artist)

        artists_data = []
        for artist in artist_results:
            artist_details = {
                'uri': artist["uri"],
                'name': artist["name"],
                'followers': f'{artist["followers"]["total"]:,}'
            }
            artists_data.append(artist_details)
        if len(artists_data) == 0:
            logger.error("No artist found")
            return None
        return artists_data

    def additional_details(self, artist_details):
        """
            Get additional details for an artist, including albums, singles, and compilations.

            Args:
                artist_details (dict): A dictionary containing details of the artist. It should include at least the following key:
                                    - 'uri' (str): The URI of the artist.

            Returns:
                dict: A modified dictionary containing additional details for the artist. The dictionary includes the following keys:
                    - 'artist_albums' (list): A list of dictionaries, each containing information about an album by the artist, including:
                        - 'artist_uri' (str): The URI of the artist.
                        - 'name' (str): The name of the album.
                        - 'uri' (str): The URI of the album.
                    - 'artist_singles' (list): A list of dictionaries, each containing information about a single by the artist, including:
                        - 'artist_uri' (str): The URI of the artist.
                        - 'name' (str): The name of the single.
                        - 'uri' (str): The URI of the single.
                    - 'artist_compilations' (list): A list of dictionaries, each containing information about a compilation by the artist, including:
                        - 'artist_uri' (str): The URI of the artist.
                        - 'name' (str): The name of the compilation.
                        - 'uri' (str): The URI of the compilation.

            """
        types = ["album", "single", "compilation"]
        for one_type in types:
            key = f"artist_{one_type}s"
            artist_details[f"{key}"] = self.sp.artist_albums(
                artist_details['uri'], album_type=f'{one_type}')
            artist_details[f"{key}"] = (artist_details[f"{key}"]["items"])
            artist_details[key] = {
                f"{one_type}": [
                    {
                        "artist_uri": artist_details["uri"],
                        "name": item['name'],
                        "uri": item['uri']} for item in artist_details[key]]}
        return artist_details

    def get_chosen_song(self, uri):
        """
            Get details of a chosen song by its URI.

            Args:
                uri (str): The URI of the song.

            Returns:
                dict: A dictionary containing details of the chosen song with the following keys:
                    - 'id' (str): The ID of the song.
                    - 'artists' (list): A list of artist names associated with the song.
                    - 'name' (str): The name/title of the song.
                    - 'album' (str): The name of the album to which the song belongs.
                    - 'release_date' (str): The release date of the album containing the song.
                    - 'total_tracks' (int): The total number of tracks in the album.
                    - 'track_no' (int): The track number of the song in the album.
                    - 'uri' (str): The URI of the song.
                    - 'preview_url' (str): The URL for a preview of the song.
                    - 'external_url' (str): The external Spotify URL for the song.
                    - 'duration_ms' (int): The duration of the song in milliseconds.
                    - 'explicit' (bool): Indicates whether the song is explicit.
                    - 'image' (str): The URL of the song's album cover image.

            Note:
                If the album or image details are not found, default values are provided.
            """
        chosen_song = self.sp.track(uri)
        track_details = {
            'id': chosen_song["id"],
            'artists': [artist["name"] for artist in chosen_song["album"]["artists"]],
            'name': chosen_song["name"],
            'album': chosen_song["album"]["name"],
            'release_date': chosen_song["album"]["release_date"],
            'total_tracks': chosen_song["album"]["total_tracks"],
            'track_no': chosen_song["track_number"],
            'uri': chosen_song["uri"],
            'preview_url': chosen_song["preview_url"],
            'external_url': chosen_song["external_urls"]["spotify"],
            'duration_ms': chosen_song["duration_ms"],
            'explicit': chosen_song["explicit"],
        }
        if chosen_song.get('album') and chosen_song['album'].get('images'):
            track_details['image'] = chosen_song['album']['images'][0]['url']
        else:
            track_details['image'] = "https://cdn.business2community.com/wp-content/uploads/2014/03/Unknown-person.gif"
            logger.info(f"No image found for track {track_details['name']}")

        return track_details

    def song(self, artist, title) -> list:
        """
            Get all possible details of a track.

            Args:
                artist (str): The name of the artist associated with the track.
                title (str): The title of the track.

            Returns:
                list: A list containing dictionaries with details of each matching track. Each dictionary
                    includes the following keys: 'artists' (string), 'name' (string), and 'uri' (string).

            Note:
                The 'artists' key in each dictionary contains a comma-separated string of artist names
                associated with the track.

            """
        track_data = self.sp.search(q=f"{artist} {title}", type="track")
        possible_tracks = track_data["tracks"]["items"]
        track_results = []
        if len(possible_tracks) == 0:
            logger.info(f"No tracks found for {artist}, {title}")
            return []
        for track in possible_tracks:
            track_details = {
                'artists': ', '.join([artist["name"] for artist in track["album"]["artists"]]),
                'name': track["name"],
                'uri': track["uri"]
            }
            track_results.append(track_details)
        return track_results

    def album(self, artist, title, uri) -> dict:
        """
            Get details of an album based on the artist, title, or URI.

            Args:
                artist (str): The name of the artist associated with the album.
                title (str): The title of the album.
                uri (str, optional): The URI (Uniform Resource Identifier) of the album. Defaults to None.

            Returns:
                dict: A dictionary containing details of the album. The dictionary includes the following keys:
                    - 'id' (str): The ID of the album.
                    - 'artists' (list): A list of artist names associated with the album.
                    - 'name' (str): The name of the album.
                    - 'release_date' (str): The release date of the album.
                    - 'total_tracks' (int): The total number of tracks in the album.
                    - 'uri' (str): The URI of the album.
                    - 'images' (str): URL of the first image associated with the album.
                    - 'album_tracks' (list): A list of dictionaries, each containing information about a track in the album, including:
                        - 'name' (str): The name of the track.
                        - 'uri' (str): The URI of the track.
                        - 'artists' (str): The name of the primary artist for the track.

                If a URI is provided, the details of the specified album are retrieved. If no matching album is found, returns None.

                If no URI is provided, a search is performed based on the artist and title. If no matching albums are found, returns None.

            """
        if uri is not None:
            try:
                chosen_album = self.sp.album(uri)
            except BaseException:
                return uri
        else:
            album_data = self.sp.search(q=f"{title}' {artist}", type="album")
            possible_albums = album_data["albums"]["items"]
            if len(possible_albums) == 0:
                logger.info("No tracks found")
                return
            # return json.dumps(possible_tracks[0], indent=4)
            chosen_album = possible_albums[0]
        album_details = {
            'id': chosen_album["id"],
            'artists': [artist["name"] for artist in chosen_album["artists"]],
            'name': chosen_album["name"],
            'release_date': chosen_album["release_date"],
            'total_tracks': chosen_album["total_tracks"],
            'uri': chosen_album["uri"],
            'images': chosen_album["images"][0]["url"],
        }
        items = self.sp.album_tracks(album_details["id"])["items"]
        album_details['album_tracks'] = [
            {
                "name": item['name'],
                "uri": item['uri'],
                "artists": item["artists"][0]["name"]} for item in items]
        return album_details

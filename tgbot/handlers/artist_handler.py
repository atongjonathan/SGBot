from telebot.types import Message
from ..utils import spotify, keyboard
from telebot import TeleBot


class ArtistHandler:
    def __init__(self, bot: TeleBot) -> None:
        self.bot = bot

    def search_artist(self, message: Message, artist: str) -> None:
        """
        Search for the artist from the string provided.

        Args:
            message: Telegram message object
            artist: Artist strings passed by the user

        Returns:
            None
        """
        artist_results = spotify.artist(artist)
        if len(artist_results) == 0:  # Handles when no artist is found
            self.bot.send_message(
                message.chat.id,
                f"Artist `{message.text}` not found!⚠. Please check your spelling and also include special characters.\nTry again.",
                reply_markup=keyboard.start_markup)
            return
        # When artists are found
        no_of_results = len(artist_results)
        result_string = [
            f"{idx+1}. `{item['name']}` ~ Followers: {item['followers']}"
            for idx, item in enumerate(artist_results)
        ]
        # Text to send the user to see the results
        result_string = '\n'.join(result_string)
        # Make keyboard for corresponding possible artists
        artists_keyboard = keyboard.keyboard_for_results(
            results=artist_results)
        self.bot.send_message(
            message.chat.id,
            f"Found {no_of_results} result(s) from the search `{artist}` ~ {message.from_user.first_name}\n\n{result_string}",
            reply_markup=artists_keyboard)

    def send_chosen_artist(self, artist_details:dict, message: Message):
        """
        Sends back the requested artist details with a reply markup for specificity of which type
        """
        caption = f'👤Artist: `{artist_details["name"]}`\n🧑Followers: `{artist_details["followers"]:,}` \n🎭Genre(s): `{", ".join(artist_details["genres"])}` \n'
        lists_of_type = [
            artist_details["artist_singles"]["single"],
            artist_details["artist_albums"]["album"],
            artist_details["artist_compilations"]["compilation"]
        ]
        # Get lengths to check if these lists requested exist for the artist
        lengths = [len(item) for item in lists_of_type]
        pin = self.bot.send_photo(message.chat.id,
                                  photo=artist_details["images"],
                                  caption=caption,
                                  reply_markup=keyboard.view_handler(
                                      artist_details["name"], artist_details["uri"],
                                      lengths))
        self.bot.pin_chat_message(message.chat.id, pin.id)



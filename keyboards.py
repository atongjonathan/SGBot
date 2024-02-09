from telebot import types
from logging import getLogger
import json
logger = getLogger(__name__)


class Keyboard():
    def __init__(self) -> None:
        self.hide_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.hide_button = types.KeyboardButton("⬆️ Show command buttons")
        self.hide_keyboard.add(self.hide_button)

        self.force_markup = types.ForceReply()

        self.start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        self.start_markup.row("⬇️ Hide command buttons")
        self.start_markup.row('/artist', '/song')

    def _make_sub_lists(self, list_of_type, items_per_page):
        items_per_page = 5
        lists = []

        for i in range(0, len(list_of_type), items_per_page):
            sublist = list_of_type[i:i + items_per_page]
            lists.append(sublist)
        return lists

    def build_menu(self, buttons, n_cols, header_buttons=None,
                   footer_buttons=None):
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, header_buttons)
        if footer_buttons:
            menu.append(footer_buttons)
        return menu

    def keyboard_for_results(self, results: list, isTrending=False, isPreview=False):
        """
        Makes keyboard for possible artists or songs

        Args:
            list: A list containing dictionaries with details of the artist/song(s) found.
        Each dictionary includes the following keys: - 'uri' (str): The URI of the artist/song. - 'name' (str): The name of the artist. - 'followers' (str): The total number of followers for the artist, formatted with commas

        Returns:
            keyboard: A keyboard with the following close button (callback_data: close_make) and results with arguements:
                - callback_data: result_{uri}
                - string: Number from the items 
        """
        close = types.InlineKeyboardButton(
            "Close", callback_data=f'close_make')
        all = types.InlineKeyboardButton(
            "Get all", callback_data=f'all_{len(results)}_{isPreview}')
        buttons = []
        for idx, result in enumerate(results):
            button = types.InlineKeyboardButton(
                str(idx + 1), callback_data=f"result_{result['uri']}")
            buttons.append(button)
        keyboard = types.InlineKeyboardMarkup(
            self.build_menu(buttons, n_cols=4))
        if isTrending:
            keyboard.add(all)
        keyboard.add(close)
        return keyboard

    def make_for_type(self, list_of_type, current_page):
        """
        Makes keyboard for a specific list and for a specific page

        Args:
            list_of_type: Normaly is a dictionary UNLESS top tracks where it is a LIST
        """
        try:  # Used to distinguish if list of type is a list of top tracks or a dict
            for key, value in list_of_type.items():
                list_of_type = value
                one_type = key  # Key is the type for future generations
        except Exception as e:  # Found to be of top tracks
            logger.info(f"Exception {e}. Handling it for toptracks case")
            one_type = "toptracks"  # Key is set to be toptracks
            pass
        pages_list = self._make_sub_lists(list_of_type, 5)
        keyboard = types.InlineKeyboardMarkup()
        if len(list_of_type) == 0:
            pass
        else:
            page = pages_list[current_page]
            for album in page:
                name = album["name"]  # Used a string visible
                # Used as callback for generation of the  album or single songs
                uri = album["uri"]
                # For pagination to know the chosen artist
                artist_uri = album["artist_uri"]
                button = types.InlineKeyboardButton(
                    f"{name}", callback_data=uri)
                keyboard.add(button)
        next = types.InlineKeyboardButton(
            "Next >>", callback_data=f'_n_{artist_uri}_{one_type}_{current_page}')  # Using data to be used for next pages
        previous = types.InlineKeyboardButton(
            "<< Previous", callback_data=f'_p_{artist_uri}_{one_type}_{current_page}')
        close = types.InlineKeyboardButton(
            "Close", callback_data=f'close_make')
        number_of_pages = len(pages_list) - 1
        if not current_page == number_of_pages and current_page < number_of_pages:
            keyboard.add(next)
        if current_page > 0:
            keyboard.add(previous)
        keyboard.add(close)
        return keyboard

    def lyrics_handler(self, artists, uri):
        keyboard = types.InlineKeyboardMarkup()
        lyrics_button = types.InlineKeyboardButton(
            text=f'Get "{artists}" lyrics', callback_data=f'lyrics_{uri}')
        keyboard.add(lyrics_button)
        return keyboard

    def link_handler(self, link):
        keyboard = types.InlineKeyboardMarkup()
        lyrics_button = types.InlineKeyboardButton(
            text=f'🚀Stream on Spotify?', url=link)
        keyboard.add(lyrics_button)
        return keyboard

    def make_for_trending(self, list_of_trending):
        keyboard = types.InlineKeyboardMarkup()
        close = types.InlineKeyboardButton(
            "Close", callback_data=f'close_make')
        for song in list_of_trending:
            name = song["name"]  # Used a string visible
            # Used as callback for generation of the  album or single songs
            uri = song["uri"]
            # artist_uri = album["artist_uri"] # For pagination to know the chosen artist
            button = types.InlineKeyboardButton(
                f"{name}", callback_data=uri)
            keyboard.add(button)
        keyboard.add(close)
        return keyboard

    def view_handler(self, name: str, uri: str, lengths: list):
        """
        Send reply markup for user to be specific on type of data required

        Args:
            - name: Name of the artist for use as string
            - uri: For artist
            - lengths: Length to determine plausibility

        Returns:
            Keyboard with all possibe list items from the artist with callback_data:"type of data speciified_the uri of the artist"

        """
        keyboard = types.InlineKeyboardMarkup()
        top_tracks_button = types.InlineKeyboardButton(
            f"Top Tracks🔝", callback_data=f"toptracks_{uri}")  # For use of uri to geberate next top_tracks
        keyboard.add(top_tracks_button)
        type = ['single', 'album', 'compilation']
        for idx, item in enumerate(lengths):
            if (item > 0):  # Make only when more than 0
                button = types.InlineKeyboardButton(
                    f"{name}'s {type[idx].title()}s🧐", callback_data=f"{type[idx]}_{uri}")  # type of data speciified for the artist of that uri
                keyboard.row(button)
        return keyboard


keyboard = Keyboard()

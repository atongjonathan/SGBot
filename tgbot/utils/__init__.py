# create your functions, database connections, and other things in this folder
from .spotify import Spotify
from .keyboard import Keyboard
from .database import Database
spotify = Spotify()
keyboard = Keyboard()
database = Database()
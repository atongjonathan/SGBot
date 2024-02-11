from tgbot.utils.database import Database
from tgbot.handlers.vars import Vars


# Admin role
class Admin():
    db = Database()
    if Vars.admins == None:
        admins = db.get_all_data("admins")
    else:
        admins = Vars.admins
    chat_ids = [admin["chat_id"] for admin in admins]




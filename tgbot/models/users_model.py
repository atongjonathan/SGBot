from tgbot.utils.database import Database


# Admin role
class Admin():
    db = Database()
    admins = db.get_all_data("admins")
    chat_ids = [admin["chat_id"] for admin in admins]




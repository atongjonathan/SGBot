import json
from pymongo import MongoClient
from telebot import logging
from tgbot.config import DATABASE
from pymongo.errors import DuplicateKeyError

class Database:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initialising database ...")
        try:
            client = MongoClient(DATABASE)
            self.db = client['sgbot']
            self.logger.info("Database initialised successfully")
        except Exception as e:
            self.logger.error(f"Error occured when connecting to database: {e}")
        

    def insert_user(self, user):
        users_collection = self.db['users']
        existing_user = users_collection.find_one({'chat_id': user['chat_id']})
        if existing_user:
                raise DuplicateKeyError(f"User with id {user['id']} already exists")
        else:
            users_collection.insert_one(user)
            self.logger.info(f"{user['first_name']} added to Database")

    def insert_json_data(self, json_data):
        json_data_collection = self.db['songs']
        json_data_collection.insert_one(json_data)
        self.logger.info(f"{json_data['title']} added to Database")

    def get_all_data(self, collection_name: str) -> list:
        data_collection = self.db[collection_name]
        cursor = data_collection.find()
        result = [item for item in cursor]
        return result


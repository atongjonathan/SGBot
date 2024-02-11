import json
from pymongo import MongoClient
from telebot import logging
from tgbot.config import DATABASE
from pymongo.errors import DuplicateKeyError

class Database:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def insert_user(self, user):
        client = MongoClient(DATABASE) 
        db = client['sgbot']  
        users_collection = db['users']
        existing_user = users_collection.find_one({'chat_id': user['chat_id']})
        if existing_user:
                raise DuplicateKeyError(f"User with id {user['id']} already exists")
        else:
            users_collection.insert_one(user)
            self.logger.info(f"{user['first_name']} added to Database")

    def insert_json_data(self, json_data):
        client = MongoClient(DATABASE) 
        db = client['sgbot']  
        json_data_collection = db['songs']
        json_data_collection.insert_one(json_data)
        self.logger.info(f"{json_data['title']} added to Database")

    def get_all_data(self, collection_name: str) -> list:
        client = MongoClient(DATABASE) 
        db = client['sgbot']  
        data_collection = db[collection_name]
        cursor = data_collection.find()
        result = [item for item in cursor]
        return result


import sqlite3
import json
from telebot import logging
class Database:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
    def create_table(self):
        conn = sqlite3.connect('channel_music.db')
        cursor = conn.cursor() 

        # Create a table with a column to store JSON documents
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS json_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data JSON
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data JSON UNIQUE
            )
        ''')    

        # Commit the changes and close the connection
        conn.commit()
        conn.close()


    def insert_user(self, user):
        conn = sqlite3.connect('channel_music.db')
        cursor = conn.cursor()       
        cursor.execute('INSERT INTO users (data) VALUES (?)', (json.dumps(user),))
        self.logger(f"{user['first_name']} added to Database")
        conn.commit()
        conn.close()


    def insert_json_data(self, json_data):
        conn = sqlite3.connect('channel_music.db')
        cursor = conn.cursor()    

        # Insert the JSON data into the table
        cursor.execute('INSERT INTO json_data (data) VALUES (?)', (json.dumps(json_data),))
        self.logger.info(f"{json_data['title']} added to Database")

        # Commit the changes and close the connection
        conn.commit()
        conn.close()


    def get_all_data(self, table:str)-> list:
        conn = sqlite3.connect('channel_music.db')
        cursor = conn.cursor()    
        # Retrieve all rows from the table
        cursor.execute(f'SELECT data FROM {table}')
        rows = cursor.fetchall()

        # Convert the JSON data back to Python objects
        result = [json.loads(row[0]) for row in rows]

        # Close the connection
        conn.close()
        return result


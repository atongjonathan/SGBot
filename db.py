import sqlite3
import json


def create_table():
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


def insert_user(user):
    conn = sqlite3.connect('channel_music.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (data) VALUES (?)', (json.dumps(user),))
    conn.commit()
    conn.close()


def insert_json_data(json_data):
    conn = sqlite3.connect('channel_music.db')
    cursor = conn.cursor()    

    # Insert the JSON data into the table
    cursor.execute('INSERT INTO json_data (data) VALUES (?)', (json.dumps(json_data),))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def get_all_data(data):
    conn = sqlite3.connect('channel_music.db')
    cursor = conn.cursor()    
    # Retrieve all rows from the table
    cursor.execute(f'SELECT data FROM {data}')
    rows = cursor.fetchall()

    # Convert the JSON data back to Python objects
    result = [json.loads(row[0]) for row in rows]

    # Close the connection
    conn.close()
    return result

create_table()
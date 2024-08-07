from datetime import datetime
import sqlite3
import socket

def get_current_time():

    """
    Retrieves the current date and time, formatted as a string in the format 'YYYY-MM-DD HH:MM:SS'.
    """

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def successful_login(name):

    """
    Logs a successful login attempt to the logins database with the user's name, 
    the current time, and the device hostname.
    """
        
    loginsDatabasePath = "database/loginsDatabase.db"
    connection = sqlite3.connect(loginsDatabasePath)
    cursor = connection.cursor()
    hostname = socket.gethostname()

    cursor.execute('''
    INSERT INTO logins (name, time, device)
    VALUES (?, ?, ?)
    ''', (name, get_current_time(), hostname))  

    connection.commit()
    connection.close()


from datetime import datetime
import sqlite3
import socket

def get_current_time():
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def successful_login(name, time):
    loginsDatabasePath = "Inventory-Management-System/database/loginsDatabase.db"
    connection = sqlite3.connect(loginsDatabasePath)
    cursor = connection.cursor()
    hostname = socket.gethostname()

    cursor.execute('''
    INSERT INTO logins (name, time, device)
    VALUES (?, ?, ?)
    ''', (name, time, hostname))  

    connection.commit()
    connection.close()


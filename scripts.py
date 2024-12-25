import json
from datetime import datetime
import pytz
import sqlite3
import os
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # текущая директория скрипта
DB_HUB = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'db_hub')
DB_HUB = SCRIPT_DIR if not (os.path.exists(DB_HUB) and os.path.isdir(DB_HUB)) else DB_HUB
DB_NAME = 'podcasts.db'
DB_PATH = f"{DB_HUB}/{DB_NAME}"


def now_time():  # Получение текущего времени по МСК
    now = datetime.now()
    tz = pytz.timezone('Europe/Moscow')
    now_moscow = now.astimezone(tz)
    current_time = now_moscow.strftime("%H:%M:%S")
    current_date = now_moscow.strftime("%Y.%m.%d")
    return current_date, current_time


def SQL_request(request, params=(), all_data=None):  # Выполнение SQL-запросов
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    if request.strip().lower().startswith('select'):
        cursor.execute(request, params)
        if all_data == None: result = cursor.fetchone()
        else: result = cursor.fetchall()
        connect.close()
        return result
    else:
        cursor.execute(request, params)
        connect.commit()
        connect.close()


def create_db(): # создание базы
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        username TEXT,
        message INTEGER,
        time_registration DATE,
        podcasts INTEGER
    )''')
    
    connect.commit()
    connect.close()
    print("База данных создана")



def registration(message):
    user_id = message.chat.id
    message_id = message.message_id

    date, time  = now_time()
    user = SQL_request("SELECT * FROM users WHERE id = ?", (user_id,))
    if user is None:
        SQL_request("""INSERT INTO users (id, message, time_registration)
                          VALUES (?, ?, ?)""", (user_id, message_id+1, date))
        print(f"Зарегистрирован новый пользователь")
    else:
        menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
        SQL_request("""UPDATE users SET message = ? WHERE id = ?""", (message_id+1, user_id))  # добавление telegram_id нового меню
        return menu_id

# ПРОВЕРКА СОЗДАНИЯ БД
if not os.path.exists(DB_PATH):
    create_db()
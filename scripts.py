import json
from datetime import datetime
import pytz
import sqlite3
import os
import random
from bs4 import BeautifulSoup
import requests

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
        podcasts JSON DEFAULT '{}'
    )''')
    
    connect.commit()
    connect.close()
    print("База данных создана")

def markdown(text, full=False):  # экранирование только для телеграма
    if full == True: special_characters = r'*|~[]()>#+-=|{}._!\\'
    else: special_characters = r'>#+-=|{}._!'
    escaped_text = ''
    for char in text:
        if char in special_characters:
            escaped_text += f'\\{char}'
        else:
            escaped_text += char
    return escaped_text


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

def save_podcast(podcast, user_id):
    podcast_id = podcast[len("https://podcast.ru/"):].strip()
    current_podcasts = SQL_request("SELECT podcasts FROM users WHERE id = ?", (user_id,))
    menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
    try:
        response = requests.get(podcast)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        podcast_title = soup.find('h1').get_text(strip=True)
    except Exception as e:
        return menu_id, f"Подкаст не найден \:\(\nУбедитесь, что ссылка правильная"

    podcast_data = json.dumps({podcast_title: podcast_id}, ensure_ascii=False)

    if current_podcasts:
        podcasts_list = json.loads(current_podcasts[0]) if current_podcasts[0] else {}
    else:
        podcasts_list = {}

    if podcast_id not in podcasts_list.values():
        podcasts_list[podcast_title] = podcast_id  # Добавляем новую запись
        updated_podcasts = json.dumps(podcasts_list, ensure_ascii=False)  # Преобразуем обратно в строку
        SQL_request("UPDATE users SET podcasts = ? WHERE id = ?", (updated_podcasts, user_id))
        podcast_title = markdown(podcast_title, True)
        text = f'Подкаст *{podcast_title}* добавлен!'
    else:
        text = f'Вы уже сохранили подкаст *{podcast_title}*!'
    text = markdown(text)    
    return menu_id, text

def delete_podcast(podcast_id, user_id):
    podcasts = SQL_request("SELECT podcasts FROM users WHERE id = ?", (user_id,))
    podcasts = json.loads(podcasts[0])
    podcast_name = next((name for name, id_ in podcasts.items() if id_ == podcast_id), None)
    del podcasts[podcast_name]
    updated_podcasts = json.dumps(podcasts)
    SQL_request("UPDATE users SET podcasts = ? WHERE id = ?", (updated_podcasts, user_id))
    return f"{podcast_name} успешно удалён из избранного"

if not os.path.exists(DB_PATH):
    create_db()
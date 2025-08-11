import requests
from bs4 import BeautifulSoup
import json
from TelegramTextApp.database import SQL_request
import TelegramTextApp
import os
from dotenv import load_dotenv
import re

URL = "https://podcast.ru"

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    DATABASE = os.getenv("DATABASE")
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    TelegramTextApp.start(TOKEN, "locale.json", DATABASE, debug=DEBUG)


def add_column():
    exists = SQL_request("SELECT 1 FROM pragma_table_info('TTA') WHERE name='podcasts'")
    
    if not exists:
        SQL_request("ALTER TABLE TTA ADD COLUMN podcasts JSON")
        print("Колонка 'podcasts' добавлена в таблицу TTA")
    else:
        print("Колонка 'podcasts' уже существует в таблице TTA")
add_column()

def save_podcast(tta_data):
    try:
        podcast_url = tta_data["podcast_url"]
        podcast_id = podcast_url[len("https://podcast.ru/"):].strip()
        
        if not re.match(r'^\d+$', podcast_id):
            return {"notification_text": "Неверный формат ID подкаста!"}
        
        try:
            response = requests.get(podcast_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('h1')
            if not title_tag:
                return {"notification_text": "Заголовок подкаста не найден!"}
            podcast_title = title_tag.get_text(strip=True)
        except Exception as e:
            return {"notification_text": f"Ошибка: {str(e)}"}
        
        current_data = SQL_request("SELECT podcasts FROM TTA WHERE telegram_id = ?", (tta_data["telegram_id"],))["podcasts"]
        
        podcasts_list = []
        if current_data:
            try:
                podcasts_list = json.loads(current_data) if isinstance(current_data, str) else current_data
            except json.JSONDecodeError:
                pass

        for podcast in podcasts_list:
            if podcast["id"] == podcast_id:
                return {"notification_text": f"Подкаст `{podcast_title}` уже сохранён!"}
            
        podcasts_list.append({
            "id": podcast_id,
            "title": podcast_title
        })
    
        updated_data = json.dumps(podcasts_list, ensure_ascii=False)
        SQL_request("UPDATE TTA SET podcasts = ? WHERE telegram_id = ?", (updated_data, tta_data["telegram_id"]))        
        return {"notification_text": f"Подкаст `{podcast_title}` добавлен!"}
    
    except Exception as e:
        return {"notification_text": f"Критическая ошибка: {str(e)}"}

def my_podcasts(tta_data):
    keyboard = {}
    try:
        row_podcasts = SQL_request("SELECT podcasts FROM TTA WHERE telegram_id = ?", (tta_data["telegram_id"],))["podcasts"]
        row_podcasts = json.loads(row_podcasts)
        if not row_podcasts:
            return keyboard
        for podcast in row_podcasts:
            keyboard[f"podcast|{podcast['id']}"] = podcast["title"]
        return keyboard
    except:
        return keyboard

def podcast_data(tta_data):
    try:
        podcast_id = tta_data["podcast_id"]
        response = requests.get(f"{URL}/{podcast_id}/info")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        podcast_title = soup.find('h1').get_text(strip=True)
        
        podcast_author_tag = soup.find('a', string=True)
        podcast_author = podcast_author_tag.get_text(strip=True) if podcast_author_tag else None
        
        podcast_image_tag = soup.find('img', class_='podcast-img')
        podcast_image_url = podcast_image_tag['src'] if podcast_image_tag else None
        
        return {"title":podcast_title, "author":podcast_author, "image":podcast_image_url, "URL":URL}
    except Exception as e:
        print(e)

def podcast_title(tta_data):
    telegram_id = tta_data["telegram_id"]
    podcast_id = tta_data["podcast_id"]

    row_podcasts = SQL_request("SELECT podcasts FROM TTA WHERE telegram_id = ?", (telegram_id,))["podcasts"]
    row_podcasts = json.loads(row_podcasts)

    for podcast in row_podcasts:
        if podcast["id"] == tta_data["podcast_id"]:
            return {"title":podcast["title"]}

def delete_podcast(tta_data):
    telegram_id = tta_data["telegram_id"]
    podcast_id = tta_data["podcast_id"]

    title = podcast_title(tta_data)

    row_podcasts = SQL_request("SELECT podcasts FROM TTA WHERE telegram_id = ?", (telegram_id,))["podcasts"]
    row_podcasts = json.loads(row_podcasts)
    
    if row_podcasts:
        updated_podcasts = [podcast for podcast in row_podcasts if podcast['id'] != podcast_id]
        SQL_request("UPDATE TTA SET podcasts = ? WHERE telegram_id = ?", (json.dumps(updated_podcasts), telegram_id))

    return {"title":title}
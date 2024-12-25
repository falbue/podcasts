import telebot

import config
import create_keyboard
from scripts import *

VERSION="test"
print(VERSION)

bot = telebot.TeleBot(config.API)

commands = [  # КОМАНДЫ
telebot.types.BotCommand("start", "Перезапуск"),
telebot.types.BotCommand("help", "Помощь"),
]
bot.set_my_commands(commands)


@bot.message_handler(commands=['start'])  # обработка команды start
def start(message):
    menu_id = registration(message)
    keyboard = create_keyboard.main()
    text = "Главное меню"
    bot.send_message(message.chat.id, text, reply_markup=keyboard)
    bot.delete_message(message.chat.id, message.id)
    if menu_id:
        try:
            bot.delete_message(message.chat.id, menu_id)
        except:
            pass

@bot.message_handler(commands=['help'])  # обработка команды start
def help(message):
    user_id = message.chat.id
    menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
    text = "Текст с помощью"
    keyboard = create_keyboard.help()
    bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard)
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    bot.delete_message(message.chat.id, message.message_id)


print(f"бот запущен...")
def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)  # Установите таймаут для перезапуска
        except Exception as e:
            print(f"Перезапуск...")

if __name__ == "__main__":
    # start_polling()
    bot.polling(none_stop=True, timeout=60)
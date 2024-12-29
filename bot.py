import telebot
from telebot import types

import config
import open_menu
from scripts import *

VERSION="1.1.0"
print(VERSION)

bot = telebot.TeleBot(config.API)

commands = [  # КОМАНДЫ
telebot.types.BotCommand("start", locale['commands']['start']),
telebot.types.BotCommand("help", locale['commands']['help']),
]
bot.set_my_commands(commands)


@bot.message_handler(commands=['start'])  # обработка команды start
def start(message):
    menu_id = registration(message)
    text, keyboard = open_menu.main(message)
    bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode="MarkdownV2")
    bot.delete_message(message.chat.id, message.id)
    if menu_id:
        try:
            bot.delete_message(message.chat.id, menu_id)
        except:
            pass

@bot.message_handler(commands=['help'])  # обработка команды help
def help(message):
    bot.delete_message(message.chat.id, message.message_id)
    user_id = message.chat.id
    menu_id = SQL_request("SELECT message FROM users WHERE id = ?", (user_id,))
    text, keyboard = open_menu.help(message)
    bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):  # работа с вызовами inline кнопок
    user_id = call.message.chat.id
    menu_id = call.message.message_id
    data = call.data
    user = SQL_request("SELECT * FROM users WHERE id = ?", (int(user_id),))
    SQL_request("UPDATE users SET message = ? WHERE id = ?", (menu_id, user_id))
    bot.clear_step_handler_by_chat_id(chat_id=user_id)
    print(f"{user_id}: {call.data}")


    if (call.data).split(":")[0] == "return":
        menu_name = (call.data).split(":")[1]
        menu_function = getattr(open_menu, menu_name)
        text, keyboard = menu_function(call)
        bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")

    elif (call.data).split(":")[0] == "open_podcast":
        podcast_id = (call.data).split(":")[1]
        text, keyboard = open_menu.open_podcast(podcast_id)
        bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")

    elif (call.data).split(":")[0] == "delete":
        podcast_id = (call.data).split(":")[1]
        text = delete_podcast(podcast_id, user_id)
        bot.answer_callback_query(call.id, text)
        text, keyboard = open_menu.save(call)
        bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")

    else:
        menu_function = getattr(open_menu, call.data)
        text, keyboard = menu_function(call)
        bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")



@bot.message_handler(func=lambda message: True)
def handle_text_message(message):
    bot.delete_message(message.chat.id, message.message_id)
    if message.text.startswith("https://podcast.ru/"):
        user_id = message.chat.id
        menu_id, text = save_podcast(message.text, user_id)
        keyboard = open_menu.save_podcast()
        bot.edit_message_text(chat_id=user_id, message_id=menu_id, text=text, reply_markup=keyboard, parse_mode="MarkdownV2")



print(f"бот запущен...")
def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Перезапуск...")

if __name__ == "__main__":
    # start_polling()
    bot.polling()
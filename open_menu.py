from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import random
from scripts import *
import json


def main(call):
    text = "Главное меню"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_save = InlineKeyboardButton("Сохранённые", callback_data='save')
    btn_random = InlineKeyboardButton("Случайный", callback_data='random')
    keyboard.add(btn_save, btn_random)
    return text, keyboard

def help(call):
    text = "Меню с помощью"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard

def save(call):
    user_id = call.message.chat.id
    podcasts = SQL_request("SELECT podcasts FROM users WHERE id = ?", (user_id,))
    if not podcasts[0]:
        text = "У Вас нет сохранённых подкастов!"
    else:
        text = "Сохранение подкастов в разработке!"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard

def random(call):
    text = "Случайные подкасты в разработке!"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard

def save_podcast():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return keyboard
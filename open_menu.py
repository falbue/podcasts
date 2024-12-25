from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types
import random


def main():
    text = "Главное меню"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_save = InlineKeyboardButton("Сохранённые", callback_data='save')
    btn_random = InlineKeyboardButton("Случайный", callback_data='random')
    keyboard.add(btn_save, btn_random)
    return text, keyboard

def help():
    text = "Меню с помощью"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard

def save():
    text = "Сохранение подкастов в разработке!"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard

def random():
    text = "Случайные подкасты в разработке!"
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return text, keyboard
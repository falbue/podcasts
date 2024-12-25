from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types


def main():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_save = InlineKeyboardButton("Сохранённые", callback_data='save')
    btn_random = InlineKeyboardButton("Случайный", callback_data='random')
    keyboard.add(btn_save, btn_random)
    return keyboard

def help():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_return = InlineKeyboardButton("< Назад", callback_data='return:main')
    keyboard.add(btn_return)
    return keyboard

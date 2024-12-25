from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot import types


def main():
    keyboard = InlineKeyboardMarkup(row_width=2)
    btn_save = InlineKeyboardButton("Сохранённые", callback_data='save')
    btn_random = InlineKeyboardButton("Случайный", callback_data='random')
    keyboard.add(btn_save, btn_random)
    return keyboard
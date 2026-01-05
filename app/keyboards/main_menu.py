from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def base_menu():
    """Базове меню - тільки кнопка повернення до сімей"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Сімʼя")]
        ],
        resize_keyboard=True
    )
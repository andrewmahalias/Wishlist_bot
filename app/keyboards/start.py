from aiogram.types import ReplyKeyboardMarkup

from app.keyboards.family import family_button


def start_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

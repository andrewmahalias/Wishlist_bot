from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def start_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Сімʼя")]
        ],
        resize_keyboard=True
    )

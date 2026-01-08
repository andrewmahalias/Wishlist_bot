from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_done_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Готово")]
        ],
        resize_keyboard=True
    )
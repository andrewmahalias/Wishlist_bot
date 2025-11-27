from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def my_wishlist_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати бажання")],
            [KeyboardButton(text="📋 Мої бажання")]
        ],
        resize_keyboard=True
    )


remove_keyboard = ReplyKeyboardRemove()

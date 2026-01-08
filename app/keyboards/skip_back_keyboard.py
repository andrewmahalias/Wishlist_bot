from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_skip_back_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавіатура з Skip і Back"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустити")],
            [KeyboardButton(text="🔙 Назад")],
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )


def get_back_cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")],
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )


def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавіатура тільки з Back (для обов'язкових полів)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


def get_done_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Готово")]
        ],
        resize_keyboard=True
    )


remove_keyboard = ReplyKeyboardRemove()

from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

from app.models.models import Wish


def navigation_keyboard(skip: bool = True) -> InlineKeyboardMarkup:
    buttons = []
    if skip:
        buttons.append([InlineKeyboardButton("⏭ Пропустити", callback_data="skip_field")])
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_field")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def my_wishlist_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Додати бажання")],
            [KeyboardButton(text="📋 Мої бажання")],
            [KeyboardButton(text="🏠 Сімʼя")],
        ],
        resize_keyboard=True
    )


def get_wishes_keyboard(wishes: List[Wish]) -> InlineKeyboardMarkup:
    buttons = []

    for wish in wishes:
        title = wish.title if len(wish.title) <= 35 else wish.title[:32] + "..."

        buttons.append([
            InlineKeyboardButton(
                text=title,
                callback_data=f"wish:{wish.id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_wishes_details_keyboard(wish: Wish) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="✏ Редагувати",
                callback_data=f"edit:{wish.id}"
            ),
            InlineKeyboardButton(
                text="🗑 Видалити",
                callback_data=f"delete_wish:{wish.id}"
            )
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

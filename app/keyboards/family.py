from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def families_kb(families: list[tuple[int, str]]):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"family:select:{fid}")]
        for fid, name in families
    ]

    buttons += [
        [InlineKeyboardButton(text="➕ Створити сім'ю", callback_data="family:create")],
        [InlineKeyboardButton(text="🔑 Приєднатися кодом", callback_data="family:join")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

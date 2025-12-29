from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def families_kb(families: list[tuple[int, str]]):
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"family:select:{fid}")]
        for fid, name in families
    ]

    buttons += [
        [InlineKeyboardButton(text="➕ Create family", callback_data="family:create")],
        [InlineKeyboardButton(text="🔑 Join by code", callback_data="family:join")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

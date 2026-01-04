from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


def families_kb(families: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    print(f"[DEBUG] families_kb отримала families: {families}")
    print(f"[DEBUG] Кількість сімей: {len(families)}")

    buttons = [
        [InlineKeyboardButton(
            text=name,
            callback_data=f"family:select:{family_id}"
        )]
        for family_id, name in families
    ]

    buttons.append([
        InlineKeyboardButton(text="➕ Створити сімʼю", callback_data="family:create"),
        InlineKeyboardButton(text="🔗 Приєднатись", callback_data="family:join"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)



def family_actions_kb(family_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Мій wishlist",
                callback_data="action:my_wishlist"
            ),
            InlineKeyboardButton(
                text="🎁 Сімейний wishlist",
                callback_data=f"action:family_wishlist:{family_id}"
            )
        ]
    ])

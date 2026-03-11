from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.family import get_family_members
from app.crud.user import get_user_by_id
from app.crud.wish import get_user_wishlist
from app.models import User

router = Router()


@router.callback_query(F.data.startswith("action:family_wishlist:"))
async def show_family_members(
        cb: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: User
):
    family_id = int(cb.data.split(":")[-1])
    family_members = await get_family_members(session, family_id)

    other_members = [member for member in family_members if member.id != user.id]

    if not other_members:
        await cb.answer("У сім'ї поки немає інших членів 😔", show_alert=True)
        return

    keyboard_buttons = []
    for member in other_members:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"👤 {member.name}",
                callback_data=f"member:wishlist:{member.id}"
            )
        ])

    keyboard_buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"family:select:{family_id}"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await cb.message.edit_text(
        "Оберіть члена сім'ї:",
        reply_markup=keyboard
    )
    await cb.answer()


@router.callback_query(F.data.startswith("member:wishlist:"))
async def show_member_wishlist(
        cb: CallbackQuery,
        session: AsyncSession,
        state: FSMContext
):
    member_id = int(cb.data.split(":")[-1])

    data = await state.get_data()
    family_id = data.get("family_id")

    wishlist = await get_user_wishlist(
        session,
        user_id=member_id,
        family_id=family_id
    )
    member = await get_user_by_id(session, member_id)

    if not wishlist:
        text = f"Wishlist {member.name} порожній 😔"
    else:
        text = f"🎁 Wishlist {member.name}:\n\n"
        for idx, item in enumerate(wishlist, 1):
            text += f"{idx}. {item.title}\n"
            if item.description:
                text += f"   {item.description}\n"
            if item.link:
                text += f"   🔗 {item.link}\n"
            if item.price:
                text += f"   💰 {item.price}\n"
            text += "\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="◀️ Назад до списку",
            callback_data=f"action:family_wishlist:{family_id}"
        )]
    ])

    await cb.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await cb.answer()

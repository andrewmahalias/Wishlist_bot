from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu, get_wishes_keyboard
from app.models.models import User, Wish

router = Router()


async def send_current_wishlist(callback: CallbackQuery, session: AsyncSession, user: User):
    """Відправляє актуальний список бажань користувача"""
    result = await session.execute(select(Wish).where(Wish.user_id == user.id))
    wishes = result.scalars().all()

    if not wishes:
        await callback.message.answer(
            "У тебе ще немає бажань.",
            reply_markup=my_wishlist_menu()
        )
    else:
        await callback.message.answer(
            f"📋 <b>Твої бажання ({len(wishes)}):</b>\nНатисни на бажання:",
            reply_markup=get_wishes_keyboard(wishes)
        )


@router.callback_query(F.data.startswith("delete_wish:"))
async def confirm_delete_wish(callback: CallbackQuery, state: FSMContext):
    wish_id = int(callback.data.split(":")[1])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Так", callback_data=f"delete_confirm:{wish_id}"),
                InlineKeyboardButton(text="❌ Ні", callback_data="delete_cancel")
            ]
        ]
    )
    await callback.message.answer(
        "Впевнені, що хочете видалити це бажання? 🏴‍☠️",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_confirm:"))
async def delete_wish(callback: CallbackQuery, session: AsyncSession, user: User):
    wish_id = int(callback.data.split(":")[1])
    result = await session.execute(
        select(Wish).where(Wish.id == wish_id, Wish.user_id == user.id)
    )
    wish = result.scalar_one_or_none()

    if wish:
        await session.delete(wish)
        await session.commit()
        await callback.message.answer("Бажання видалено 🗑")
    else:
        await callback.message.answer("Бажання не знайдено 😕")

    await send_current_wishlist(callback, session, user)
    await callback.answer()


@router.callback_query(F.data == "delete_cancel")
async def cancel_delete(callback: CallbackQuery, session: AsyncSession, user: User):
    await callback.message.answer("Видалення скасовано 😉")

    await send_current_wishlist(callback, session, user)
    await callback.answer()

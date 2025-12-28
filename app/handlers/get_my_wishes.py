from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import (
    my_wishlist_menu,
    get_wishes_keyboard,
    get_wishes_details_keyboard,
)
from app.models.models import User, Wish
from app.states.wishlist_states import WishListState

router = Router()


@router.message(F.text == "📋 Мої бажання")
async def show_my_wishes(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
):
    data = await state.get_data()
    family_id = data.get("family_id")

    if not family_id:
        await message.answer("Спочатку обери сімʼю.")
        return

    await state.set_state(WishListState.viewing)

    result = await session.execute(
        select(Wish).where(
            Wish.user_id == user.id,
            Wish.family_id == family_id,
        )
    )
    wishes = result.scalars().all()

    if not wishes:
        await message.answer(
            "У цій сімʼї у тебе ще немає бажань.",
            reply_markup=my_wishlist_menu(),
        )
        return

    await message.answer(
        f"📋 <b>Твої бажання ({len(wishes)}):</b>\nНатисни на бажання:",
        reply_markup=get_wishes_keyboard(wishes),
        parse_mode="HTML",
    )


@router.callback_query(
    WishListState.viewing,
    F.data.startswith("wish:")
)
async def show_wish_details(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
):
    data = await state.get_data()
    family_id = data.get("family_id")

    if not family_id:
        await callback.answer("Сімʼя не вибрана", show_alert=True)
        return

    try:
        wish_id = int(callback.data.split(":")[1])
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    result = await session.execute(
        select(Wish).where(
            Wish.id == wish_id,
            Wish.user_id == user.id,
            Wish.family_id == family_id,
        )
    )
    wish = result.scalar_one_or_none()

    if not wish:
        await callback.answer("Бажання не знайдено", show_alert=True)
        return

    text = f"<b>{wish.title}</b>\n\n"

    if wish.description:
        text += f"📝 {wish.description}\n\n"

    if wish.link:
        text += f"🔗 <a href='{wish.link}'>Перейти за посиланням</a>\n\n"

    if wish.price is not None:
        text += f"💰 €{wish.price}"

    await callback.message.answer(
        text,
        reply_markup=get_wishes_details_keyboard(wish),
        parse_mode="HTML",
    )
    await callback.answer()

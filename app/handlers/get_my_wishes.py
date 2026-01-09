import html

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import (
    get_wishes_keyboard,
    get_wishes_details_keyboard, my_wishlist_menu,
)
from app.models.models import User, Wish
from app.states.wishlist_states import WishListState

router = Router()


@router.callback_query(F.data == "action:my_wishlist")
async def show_my_wishlist_menu(
        cb: CallbackQuery,
        state: FSMContext,
):
    data = await state.get_data()
    family_id = data.get("family_id")

    if not family_id:
        await cb.answer("Спочатку обери сімʼю", show_alert=True)
        return

    # Показуємо повне меню для wishlist
    await cb.message.answer(
        "Обери дію, використовуючи кнопки 👇:",
        reply_markup=my_wishlist_menu()
    )

    await cb.message.delete()
    await cb.answer()


@router.callback_query(F.data == "action:back_to_my_wishlist")
async def back_to_my_wishlist(
        cb: CallbackQuery,
        session: AsyncSession,
        user: User,
        state: FSMContext,
):
    data = await state.get_data()
    family_id = data.get("family_id")

    if not family_id:
        await cb.answer("Спочатку обери сімʼю", show_alert=True)
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
        await cb.message.edit_text(
            "У цій сімʼї у тебе ще немає бажань",
            reply_markup=my_wishlist_menu(),
        )
        await cb.answer()
        return

    await cb.message.edit_text(
        f"📋 <b>Твої бажання ({len(wishes)}):</b>\nНатисни на бажання:",
        reply_markup=get_wishes_keyboard(wishes),
        parse_mode="HTML",
    )
    await cb.answer()


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
        await message.answer("Спочатку обери сімʼю")
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
            "У цій сімʼї у тебе ще немає бажань",
            reply_markup=my_wishlist_menu(),
        )
        return

    # Зберігаємо ID повідомлення зі списком
    sent_msg = await message.answer(
        f"📋 <b>Твої бажання ({len(wishes)}):</b>\nНатисни на бажання:",
        reply_markup=get_wishes_keyboard(wishes),
        parse_mode="HTML",
    )

    # Зберігаємо message_id для подальшого використання
    await state.update_data(wishes_list_message_id=sent_msg.message_id)


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

    text = f"<b>{html.escape(wish.title)}</b>\n\n"

    if wish.description:
        text += f"📝 {html.escape(wish.description)}\n\n"

    if wish.link:
        text += f"🔗 <a href='{html.escape(wish.link)}'>Посилання</a>\n\n"

    if wish.price is not None:
        text += f"💰 €{html.escape(str(wish.price))}"

    keyboard_builder = InlineKeyboardBuilder.from_markup(
        get_wishes_details_keyboard(wish)
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="◀️ Назад до списку",
            callback_data="action:back_to_my_wishlist"
        )
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()

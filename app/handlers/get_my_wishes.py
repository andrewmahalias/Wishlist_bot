from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
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
        await cb.answer("Спочатку обери сімʼю.", show_alert=True)
        return

    # Показуємо повне меню для wishlist
    await cb.message.answer(
        "Обери дію:",
        reply_markup=my_wishlist_menu()
    )

    # Видаляємо попереднє inline меню
    await cb.message.delete()
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
    detail_message_id = data.get("detail_message_id")

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
        text += f"🔗 <a href='{wish.link}'>Посилання</a>\n\n"

    if wish.price is not None:
        text += f"💰 €{wish.price}"

    # Якщо є попереднє повідомлення з деталями - видаляємо його
    if detail_message_id:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=detail_message_id
            )
        except Exception:
            pass  # Ігноруємо помилки видалення

    # Завжди створюємо нове повідомлення після списку
    sent_msg = await callback.message.answer(
        text,
        reply_markup=get_wishes_details_keyboard(wish),
        parse_mode="HTML",
    )
    await state.update_data(detail_message_id=sent_msg.message_id)
    await callback.answer()
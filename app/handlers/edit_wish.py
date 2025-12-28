from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu
from app.keyboards.skip_back_keyboard import get_skip_back_keyboard
from app.models.models import Wish, User
from app.states.wishlist_states import EditWishState

router = Router()


@router.callback_query(F.data.startswith("edit:"))
async def start_edit(callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User):
    wish_id = int(callback.data.split(":")[1])
    result = await session.execute(
        select(Wish).where(Wish.id == wish_id, Wish.user_id == user.id)
    )
    wish = result.scalar_one_or_none()

    if not wish:
        await callback.message.answer("Бажання не знайдено 😕")
        await callback.answer()
        return

    await state.update_data(
        wish_id=wish.id,
        original_title=wish.title,
        original_description=wish.description,
        original_link=wish.link,
        original_price=wish.price
    )
    await state.set_state(EditWishState.title)
    await callback.message.answer(
        f"✏️ Редагуємо бажання: <b>{wish.title}</b>\n\nВведи нову назву:",
        reply_markup=get_skip_back_keyboard()
    )
    await callback.answer()


@router.message(EditWishState.title)
async def edit_title(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return

    await state.update_data(title=message.text)
    await state.set_state(EditWishState.description)
    await message.answer(
        "📝 Введи новий опис:",
        reply_markup=get_skip_back_keyboard()
    )


@router.message(EditWishState.description)
async def edit_description(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return

    await state.update_data(description=message.text)
    await state.set_state(EditWishState.link)
    await message.answer(
        "🔗 Введи нове посилання:",
        reply_markup=get_skip_back_keyboard()
    )


@router.message(EditWishState.link)
async def edit_link(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return

    await state.update_data(link=message.text)
    await state.set_state(EditWishState.price)
    await message.answer(
        "💰 Введи нову ціну:",
        reply_markup=get_skip_back_keyboard()
    )


@router.message(EditWishState.price)
async def edit_price(message: Message, state: FSMContext, session: AsyncSession = None, user: User = None):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return

    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Введи число:")
        return
    await state.update_data(price=price)
    await finalize_edit_wish(message, state, session, user)


async def finalize_edit_wish(message: Message, state: FSMContext, session: AsyncSession, user: User):
    """Збереження змін"""
    data = await state.get_data()
    wish_id = data["wish_id"]

    result = await session.execute(
        select(Wish).where(Wish.id == wish_id, Wish.user_id == user.id)
    )
    wish = result.scalar_one_or_none()

    if not wish:
        await message.answer("Бажання не знайдено 😕")
        await state.clear()
        return

    wish.title = data.get("title")
    wish.description = data.get("description")
    wish.link = data.get("link")
    wish.price = data.get("price")

    session.add(wish)
    await session.commit()

    await state.clear()
    await message.answer(
        "✅ Бажання оновлено!",
        reply_markup=my_wishlist_menu()
    )

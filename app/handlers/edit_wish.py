from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu
from app.models.models import Wish
from app.states.wishlist_states import EditWish

router = Router()


@router.callback_query(F.data.startswith("edit:"))
async def start_edit(callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User):
    wish_id = int(callback.data.split(":")[1])
    result = await session.execute(select(Wish).where(Wish.id == wish_id, Wish.user_id == user.id))
    wish = result.scalar_one_or_none()

    if not wish:
        await callback.message.answer("Бажання не знайдено 😕")
        await callback.answer()
        return

    await state.update_data(wish_id=wish.id)
    await state.set_state(EditWish.title)
    await callback.message.answer(f"Редагуємо бажання: <b>{wish.title}</b>\n\nВведи нову назву:")
    await callback.answer()


@router.message(EditWish.title)
async def edit_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(EditWish.description)
    await message.answer("Введи новий опис бажання:")


@router.message(EditWish.description)
async def edit_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EditWish.link)
    await message.answer("Введи нове посилання (або '-' якщо немає):")


@router.message(EditWish.link)
async def edit_link(message: Message, state: FSMContext):
    link = message.text if message.text != "-" else None
    await state.update_data(link=link)
    await state.set_state(EditWish.price)
    await message.answer("Введи нову ціну (або '-' якщо не вказано):")


@router.message(EditWish.price)
async def edit_price(message: Message, state: FSMContext, session: AsyncSession, user: User):
    data = await state.get_data()
    wish_id = data["wish_id"]

    result = await session.execute(select(Wish).where(Wish.id == wish_id, Wish.user_id == user.id))
    wish = result.scalar_one_or_none()

    if not wish:
        await message.answer("Бажання не знайдено 😕")
        await state.clear()
        return

    wish.title = data.get("title")
    wish.description = data.get("description")
    wish.link = data.get("link")
    try:
        wish.price = float(message.text) if message.text != "-" else None
    except ValueError:
        wish.price = None

    session.add(wish)
    await session.commit()

    await message.answer("Бажання успішно оновлено ✅", reply_markup=my_wishlist_menu())
    await state.clear()

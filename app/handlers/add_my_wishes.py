import html
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu
from app.keyboards.skip_back_keyboard import get_back_keyboard, get_skip_back_cancel_keyboard
from app.models.models import User, Wish
from app.states.wishlist_states import AddWishState

router = Router()


@router.message(F.text == "➕ Додати бажання")
async def start_add_wish(message: Message, state: FSMContext):
    # Зберігаємо family_id перед clear
    data = await state.get_data()
    family_id = data.get('family_id')

    if not family_id:
        await message.answer(
            "❌ Спочатку обери сімʼю через 🏠 Сімʼя"
        )
        return

    # Очищаємо state але зберігаємо family_id
    await state.clear()
    await state.update_data(family_id=family_id)

    await state.set_state(AddWishState.title)
    await message.answer(
        "📝 Крок 1/4: Введи назву бажання:",
        reply_markup=get_back_keyboard()
    )


@router.message(AddWishState.title)
async def process_title(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return
    await state.update_data(title=message.text)
    await state.set_state(AddWishState.description)
    await message.answer(
        "📝 Крок 2/4: Додай опис:",
        reply_markup=get_skip_back_cancel_keyboard()
    )


@router.message(AddWishState.description)
async def process_description(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return
    await state.update_data(description=message.text)
    await state.set_state(AddWishState.link)
    await message.answer(
        "🔗 Крок 3/4: Додай посилання:",
        reply_markup=get_skip_back_cancel_keyboard()
    )


@router.message(AddWishState.link)
async def process_link(message: Message, state: FSMContext):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return
    await state.update_data(link=message.text)
    await state.set_state(AddWishState.price)
    await message.answer(
        "💰 Крок 4/4: Вкажи ціну:",
        reply_markup=get_skip_back_cancel_keyboard()
    )


@router.message(AddWishState.price)
async def process_price(message: Message, state: FSMContext, session: AsyncSession, user: User):
    if message.text in ["🔙 Назад", "❌ Скасувати", "⏭ Пропустити"]:
        return
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Введи число (€):")
        return
    await state.update_data(price=price)
    await finalize_add_wish(message, state, session, user)


async def finalize_add_wish(message: Message, state: FSMContext, session: AsyncSession = None, user: User = None):
    """Збереження нового бажання"""
    data = await state.get_data()
    family_id = data.get('family_id')  # ← Отримуємо family_id зі стейту

    if not family_id:
        await message.answer(
            "❌ Сім'я не обрана. Спочатку обери сімʼю через 🏠 Сімʼя",
            reply_markup=my_wishlist_menu()
        )
        await state.clear()
        return

    wish = Wish(
        user_id=user.id,
        family_id=family_id,  # ← Додаємо family_id
        title=data['title'],
        description=data.get('description'),
        link=data.get('link'),
        price=data.get('price'),
        status='active'
    )

    session.add(wish)
    await session.commit()

    await state.clear()
    # Зберігаємо family_id після clear
    await state.update_data(family_id=family_id)

    # Екрануємо всі дані від користувача
    safe_title = html.escape(wish.title)
    text = f"✅ Бажання додано!\n\n"
    text += f"📌 <b>{safe_title}</b>\n"

    if wish.description:
        safe_description = html.escape(wish.description)
        text += f"📝 {safe_description}\n"

    if wish.link:
        safe_link = html.escape(wish.link)
        text += f"🔗 {safe_link}\n"

    if wish.price:
        safe_price = html.escape(str(wish.price))
        text += f"💰 €{safe_price}"

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=my_wishlist_menu()
    )
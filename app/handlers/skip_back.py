from aiogram import Router, F
from aiogram.types import Message, User
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu
from app.keyboards.skip_back_keyboard import get_skip_back_keyboard, get_back_keyboard
from app.states.wishlist_states import AddWishState, EditWish

router = Router()


@router.message(F.text == "❌ Скасувати")
async def cancel_any_fsm(message: Message, state: FSMContext):
    """Скасувати будь-який FSM"""
    current = await state.get_state()

    if current is None:
        return

    await state.clear()
    await message.answer(
        "❌ Скасовано",
        reply_markup=my_wishlist_menu()
    )


@router.message(F.text == "⏭ Пропустити")
async def skip_step(message: Message, state: FSMContext, session: AsyncSession, user: User):
    """Пропустити крок"""
    current = await state.get_state()

    if not current:
        return

    if current == AddWishState.description.state:
        await state.update_data(description=None)
        await state.set_state(AddWishState.link)
        await message.answer(
            "🔗 Крок 3/4: Додай посилання:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == AddWishState.link.state:
        await state.update_data(link=None)
        await state.set_state(AddWishState.price)
        await message.answer(
            "💰 Крок 4/4: Вкажи ціну (в грн):",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == AddWishState.price.state:
        await state.update_data(price=None)
        from app.handlers.add_my_wishes import finalize_add_wish
        await finalize_add_wish(message, state, session, user)

    elif current == EditWish.title.state:
        data = await state.get_data()
        await state.update_data(title=data.get('original_title'))
        await state.set_state(EditWish.description)
        await message.answer(
            "📝 Введи новий опис:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.description.state:
        data = await state.get_data()
        await state.update_data(description=data.get('original_description'))
        await state.set_state(EditWish.link)
        await message.answer(
            "🔗 Введи нове посилання:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.link.state:
        data = await state.get_data()
        await state.update_data(link=data.get('original_link'))
        await state.set_state(EditWish.price)
        await message.answer(
            "💰 Введи нову ціну:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.price.state:
        data = await state.get_data()
        await state.update_data(price=data.get('original_price'))
        # Викликаємо збереження
        from app.handlers.edit_wish import finalize_edit_wish
        await finalize_edit_wish(message, state, session, user)

    else:
        await message.answer("❌ Цей крок обов'язковий")


@router.message(F.text == "🔙 Назад")
async def go_back(message: Message, state: FSMContext):
    """Назад на попередній крок"""
    current = await state.get_state()

    if not current:
        return

    if current == AddWishState.description.state:
        await state.set_state(AddWishState.title)
        await message.answer(
            "📝 Крок 1/4: Введи назву бажання:",
            reply_markup=get_back_keyboard()
        )

    elif current == AddWishState.link.state:
        await state.set_state(AddWishState.description)
        await message.answer(
            "📝 Крок 2/4: Додай опис:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == AddWishState.price.state:
        await state.set_state(AddWishState.link)
        await message.answer(
            "🔗 Крок 3/4: Додай посилання:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == AddWishState.title.state:
        await state.clear()
        await message.answer("❌ Скасовано", reply_markup=my_wishlist_menu())

    # EditWish - редагування
    elif current == EditWish.description.state:
        await state.set_state(EditWish.title)
        await message.answer(
            "📝 Введи нову назву:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.link.state:
        await state.set_state(EditWish.description)
        await message.answer(
            "📝 Введи новий опис:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.price.state:
        await state.set_state(EditWish.link)
        await message.answer(
            "🔗 Введи нове посилання:",
            reply_markup=get_skip_back_keyboard()
        )

    elif current == EditWish.title.state:
        await state.clear()
        await message.answer("❌ Скасовано", reply_markup=my_wishlist_menu())

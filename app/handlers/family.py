from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.family import families_kb
from app.models.models import User
from app.services.family_service import (
    get_user_families,
    create_family,
    join_family,
)
from app.states.wishlist_states import FamilyState

router = Router()


@router.message(F.text == "🏠 Сімʼя")
async def family_menu(
        message: Message,
        session: AsyncSession,
        user: User,
):
    families = await get_user_families(session, user.id)

    await message.answer(
        "Оберіть сімʼю:",
        reply_markup=families_kb(
            [(f.id, f.name) for f in families]
        )
    )


@router.callback_query(F.data.startswith("family:select:"))
async def select_family(cb: CallbackQuery, state: FSMContext):
    family_id = int(cb.data.split(":")[-1])
    await state.update_data(family_id=family_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
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

    await cb.message.edit_text(
        "Сім’я обрана ✅\nОбери дію:",
        reply_markup=keyboard
    )
    await cb.answer()


@router.callback_query(F.data == "family:create")
async def start_create(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.creating)
    await cb.message.edit_text("Enter family name:")
    await cb.answer()


@router.message(FamilyState.creating)
async def create_family_handler(
        message: Message,
        state: FSMContext,
        user: User,
        session: AsyncSession,
):
    family = await create_family(session, user.id, message.text.strip())
    await state.clear()

    await message.answer(
        f"Сімʼю створено ✅\nКод запрошення: `{family.invite_code}`",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "family:join")
async def start_join(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.joining)
    await cb.message.edit_text("Введіть код запрошення:")
    await cb.answer()


@router.message(FamilyState.joining)
async def join_family_handler(
        message: Message,
        state: FSMContext,
        user: User,
        session: AsyncSession,
):
    family = await join_family(session, user.id, message.text.strip().upper())

    if not family:
        await message.answer("Невірний код ❌")
        return

    await state.clear()
    await message.answer(f"Ви приєднались до сімʼї «{family.name}» ✅")

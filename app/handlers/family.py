from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.models.models import User
from app.states.wishlist_states import FamilyState
from app.keyboards.family import families_kb
from app.services.family_service import (
    get_user_families,
    create_family,
    join_family,
)

router = Router()


@router.message(F.text == "🏠 Families")
async def families_entry(message: Message, state: FSMContext, user: User):
    families = await get_user_families(user.id)

    if not families:
        await message.answer("No families yet. Enter name to create one:")
        await state.set_state(FamilyState.creating)
        return

    await state.set_state(FamilyState.choosing)
    await message.answer(
        "Choose family:",
        reply_markup=families_kb(families)
    )


@router.callback_query(F.data.startswith("family:select:"))
async def select_family(cb: CallbackQuery, state: FSMContext):
    family_id = int(cb.data.split(":")[-1])
    await state.update_data(family_id=family_id)
    await state.clear()

    await cb.message.edit_text("Family selected ✅")


@router.callback_query(F.data == "family:create")
async def start_create(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.creating)
    await cb.message.edit_text("Enter family name:")


@router.message(FamilyState.creating)
async def create_family_handler(message: Message, state: FSMContext, user: User):
    family = await create_family(user.id, message.text.strip())

    await state.update_data(family_id=family.id)
    await state.clear()

    await message.answer(
        f"Family created ✅\nInvite code: `{family.invite_code}`",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "family:join")
async def start_join(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(FamilyState.joining)

    await cb.message.edit_text(
        "Enter invite code:",
        reply_markup=None
    )
    await cb.answer() #todo:


@router.message(FamilyState.joining)
async def join_family_handler(
        message: Message,
        state: FSMContext,
        user: User,
):
    invite_code = message.text.strip().upper()

    family = await join_family(user.id, invite_code)

    if not family:
        await message.answer("Invalid invite code ❌")
        return

    await state.clear()

    await message.answer(
        f"You are in family «{family.name}» ✅"
    )

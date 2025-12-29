from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.states.wishlist_states import FamilyState
from app.keyboards.family import families_kb
from app.services.family_service import (
    get_user_families,
    create_family,
    join_family,
)

router = Router()


@router.message(F.text == "🏠 Families")
async def families_entry(message: Message, state: FSMContext):
    families = await get_user_families(message.from_user.id)

    if not families:
        await message.answer("No families yet. Create one:")
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
    await cb.message.edit_text("Family selected ✅")


@router.callback_query(F.data == "family:create")
async def start_create(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.creating)
    await cb.message.edit_text("Enter family name:")


@router.message(FamilyState.creating)
async def create_family_handler(message: Message, state: FSMContext):
    family = await create_family(message.from_user.id, message.text)
    await state.update_data(family_id=family.id)
    await state.clear()

    await message.answer(
        f"Family created ✅\nInvite code: `{family.invite_code}`",
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "family:join")
async def start_join(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.joining)
    await cb.message.edit_text("Enter invite code:")


@router.message(FamilyState.joining)
async def join_family_handler(message: Message, state: FSMContext):
    family = await join_family(message.from_user.id, message.text.strip().upper())

    if not family:
        await message.answer("Invalid invite code ❌")
        return

    await state.update_data(family_id=family.id)
    await state.clear()
    await message.answer(f"Joined family «{family.name}» ✅")

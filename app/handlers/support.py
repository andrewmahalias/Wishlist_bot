from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.services.support import send_feedback_to_admin
from app.states.wishlist_states import SupportStates

router = Router()


@router.message(Command("support"))
async def support_command(message: Message, state: FSMContext):
    await message.answer("Дякую за звернення! Напишіть своє питання або фідбек 👇")
    await state.set_state(SupportStates.waiting_for_feedback)


@router.message(SupportStates.waiting_for_feedback)
async def receive_feedback(message: Message, state: FSMContext, bot: Bot):
    await send_feedback_to_admin(bot, message)
    await message.answer("Дякуємо! Ваш фідбек отримано ✅")
    await state.clear()

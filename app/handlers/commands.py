from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.start import start_kb
from app.models.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привіт, {user.name}!\n\n"
        f"Я допоможу тобі зберігати список бажань.\n"
        f"Натисни на кнопку 'Сімʼя' 🏠 для переходу в меню сімей.",
        reply_markup=start_kb()
    )

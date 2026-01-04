from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.my_wishlist import my_wishlist_menu
from app.keyboards.start import start_kb
from app.models.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привіт, {user.name}!\n\n"
        f"Я допоможу тобі зберігати список бажань.\n"
        f"Обери дію 👇",
        reply_markup=start_kb()
    )

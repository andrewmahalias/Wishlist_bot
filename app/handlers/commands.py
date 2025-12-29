from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from app.keyboards.family import families_kb
from app.keyboards.my_wishlist import my_wishlist_menu
from app.models.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, state: FSMContext):
    await state.clear()
    await message.answer(
        f"👋 Привіт, {user.name}!\n\n"
        f"Я допоможу тобі зберігати список бажань.\n\n"
        f"Обери в Меню відповідну команду\n"
        f"👉 /my_wishlist - переглянути мої бажання\n"
        f"👉 /family_wishlist - переглянути бажання сім'ї\n",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Command("my_wishlist"))
async def cmd_my_wishlist(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Виберіть дію:",
        reply_markup=my_wishlist_menu()
    )

@router.message(Command("family_wishlist"))
async def cmd_family_wishlist(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Виберіть дію:",
        reply_markup=families_kb(families=[])
    )

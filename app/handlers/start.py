from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.models.models import User

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, user: User):
    await message.answer(
        f"👋 Привіт, {user.name}!\n\n"
        f"Я допоможу тобі зберігати список бажань.\n\n"
        f"Обери в Меню відповідну команду\n"
        f"👉 /my_wishlist - переглянути мої бажання\n"
        f"👉 /family_wishlist - переглянути бажання сім'ї\n"
    )

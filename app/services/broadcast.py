from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.exceptions import TelegramForbiddenError

from app.models.models import User


async def broadcast(
    bot: Bot,
    session: AsyncSession,
    text: str,
):
    result = await session.execute(select(User.telegram_id))
    user_ids = result.scalars().all()

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
        except TelegramForbiddenError:
            # користувач заблокував бота — ігноруємо
            continue

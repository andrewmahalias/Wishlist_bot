import asyncio
import os

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramRetryAfter
from app.config import ADMIN_IDS
from app.models.models import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
BROADCAST_FILE = "app/data/broadcasts.txt"
os.makedirs(os.path.dirname(BROADCAST_FILE), exist_ok=True)


@router.message(Command("notify"))
async def notify_all(message: Message, session: AsyncSession):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Ви не адмін")
        return

    # Беремо текст після команди
    text = message.text[len("/notify"):].strip()
    if not text:
        await message.answer(
            "Будь ласка, додайте текст повідомлення після команди.\n"
            "Приклад:\n/notify <b>Оновлення!</b> Нові функції..."
        )
        return

    # Зберігаємо HTML-текст у файл
    with open(BROADCAST_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n---\n")

    # Отримуємо всіх користувачів
    users = await session.scalars(select(User.telegram_id))
    users = users.all()

    sent = 0
    for telegram_id in users:
        try:
            await message.bot.send_message(
                telegram_id,
                text,
                parse_mode=None,
            )
            sent += 1
            await asyncio.sleep(0.05)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            pass

    await message.answer(f"Розсилка завершена. Надіслано: {sent}")

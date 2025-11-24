import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.database.base import init_db
from app.handlers import start
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(AuthMiddleware())

    dp.include_router(start.router)
    # dp.include_router(my_wishlist.router)
    # dp.include_router(family_wishlist.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

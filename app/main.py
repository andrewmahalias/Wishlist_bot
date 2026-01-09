import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import BOT_TOKEN
from app.database.base import init_db
from app.handlers import (
    commands,
    add_my_wishes,
    get_my_wishes,
    delete_wish,
    edit_wish,
    skip_back_cancel,
    family,
    members,
    support,
)
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)


async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(
        commands=[
            types.BotCommand(command="start", description="Знайомство з ботом"),
            types.BotCommand(command="support", description="Зв’язатись з службою підтримки"),
        ],
        scope=types.BotCommandScopeAllPrivateChats(),
    )
    logging.info("Bot commands set")


async def main():
    await init_db()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # middlewares
    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(AuthMiddleware())

    dp.callback_query.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # routers
    dp.include_router(commands.router)
    dp.include_router(family.router)
    dp.include_router(members.router)
    dp.include_router(skip_back_cancel.router)
    dp.include_router(add_my_wishes.router)
    dp.include_router(get_my_wishes.router)
    dp.include_router(delete_wish.router)
    dp.include_router(edit_wish.router)
    dp.include_router(support.router)

    # IMPORTANT PART
    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

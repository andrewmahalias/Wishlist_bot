# app/middlewares/auth.py
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import get_or_create_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message):
            if event.from_user:
                session = data.get('session')

                if session:
                    user = await get_or_create_user(
                        session=session,
                        telegram_id=event.from_user.id,
                        name=event.from_user.full_name
                    )
                    data['user'] = user

        result = await handler(event, data)
        return result

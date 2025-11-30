from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud import get_or_create_user


class AuthMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:

        from_user = None

        if isinstance(event, Message):
            from_user = event.from_user
        elif isinstance(event, CallbackQuery):
            from_user = event.from_user

        if from_user:
            session: AsyncSession = data.get('session')

            if session:
                user = await get_or_create_user(
                    session=session,
                    telegram_id=from_user.id,
                    name=from_user.full_name
                )
                data['user'] = user

        return await handler(event, data)

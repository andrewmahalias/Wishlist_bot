from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User


async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        name: str
) -> User:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=telegram_id,
            name=name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


async def get_user_by_telegram_id(
        session: AsyncSession,
        telegram_id: int
) -> User | None:
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()

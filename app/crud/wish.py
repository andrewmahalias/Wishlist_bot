from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wish

async def create_wish(
    session: AsyncSession,
    *,
    user_id: int,
    family_id: int,
    title: str,
    description: str | None = None,
    link: str | None = None,
    price: float | None = None,
) -> Wish:
    wish = Wish(
        user_id=user_id,
        family_id=family_id,
        title=title,
        description=description,
        link=link,
        price=price,
    )
    session.add(wish)
    await session.commit()
    await session.refresh(wish)
    return wish


async def get_user_wishlist(
    session: AsyncSession,
    *,
    user_id: int,
    family_id: int,
) -> list[Wish]:
    result = await session.execute(
        select(Wish).where(
            Wish.user_id == user_id,
            Wish.family_id == family_id,
        )
    )
    return list(result.scalars().all())

async def get_user_wishlist(
    session: AsyncSession,
    *,
    user_id: int,
    family_id: int,
) -> list[Wish]:
    result = await session.execute(
        select(Wish).where(
            Wish.user_id == user_id,
            Wish.family_id == family_id,
        )
    )
    return list(result.scalars().all())

async def update_wish(
    session: AsyncSession,
    *,
    wish_id: int,
    family_id: int,
    title: str | None = None,
    description: str | None = None,
    link: str | None = None,
    price: float | None = None,
) -> None:
    values = {
        k: v for k, v in {
            "title": title,
            "description": description,
            "link": link,
            "price": price,
        }.items()
        if v is not None
    }

    if not values:
        return

    await session.execute(
        update(Wish)
        .where(
            Wish.id == wish_id,
            Wish.family_id == family_id,
        )
        .values(**values)
    )
    await session.commit()

async def delete_wish(
    session: AsyncSession,
    *,
    wish_id: int,
    family_id: int,
) -> None:
    await session.execute(
        delete(Wish).where(
            Wish.id == wish_id,
            Wish.family_id == family_id,
        )
    )
    await session.commit()



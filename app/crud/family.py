from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models import Family, family_members, User, Wish


async def create_family(
        session: AsyncSession,
        *,
        name: str,
        invite_code: str,
        owner_user_id: int,
) -> Family:
    family = Family(name=name, invite_code=invite_code)
    session.add(family)
    await session.flush()

    await session.execute(
        family_members.insert().values(
            user_id=owner_user_id,
            family_id=family.id,
            role="admin",
        )
    )

    await session.commit()
    await session.refresh(family)
    return family


async def get_family_by_id(
        session: AsyncSession,
        family_id: int,
) -> Family | None:
    result = await session.execute(
        select(Family).where(Family.id == family_id)
    )
    return result.scalar_one_or_none()


async def get_family_by_invite_code(
        session: AsyncSession,
        invite_code: str,
) -> Family | None:
    result = await session.execute(
        select(Family).where(Family.invite_code == invite_code)
    )
    return result.scalar_one_or_none()


async def get_user_families(
        session: AsyncSession,
        user_id: int,
) -> list[Family]:
    result = await session.execute(
        select(Family)
        .join(family_members)
        .where(family_members.c.user_id == user_id)
    )
    return list(result.scalars().all())


async def add_user_to_family(
        session: AsyncSession,
        *,
        user_id: int,
        family_id: int,
        role: str = "member",
) -> None:
    await session.execute(
        family_members.insert().values(
            user_id=user_id,
            family_id=family_id,
            role=role,
        )
    )
    await session.commit()


async def rename_family(
        session: AsyncSession,
        *,
        family_id: int,
        new_name: str,
) -> None:
    family = await get_family_by_id(session, family_id)
    if not family:
        return

    family.name = new_name
    await session.commit()


async def delete_family(
        session: AsyncSession,
        family_id: int,
) -> None:
    family = await get_family_by_id(session, family_id)
    if not family:
        return

    await session.delete(family)
    await session.commit()

async def get_family_wishes(
    session: AsyncSession,
    family_id: int,
) -> list[Wish]:
    result = await session.execute(
        select(Wish)
        .where(Wish.family_id == family_id)
        .order_by(Wish.created_at.desc())
    )
    return list(result.scalars().all())

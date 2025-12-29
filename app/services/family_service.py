from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.database.base import SessionLocal as async_session
from app.models import Family, family_members
import secrets
import string


def generate_invite_code(length=8):
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


async def get_user_families(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Family.id, Family.name)
            .join(family_members)
            .where(family_members.c.user_id == user_id)
        )
        return result.all()


async def create_family(user_id: int, name: str) -> Family:
    async with async_session() as session:
        family = Family(
            name=name,
            invite_code=generate_invite_code()
        )
        session.add(family)
        await session.flush()

        await session.execute(
            family_members.insert().values(
                user_id=user_id,
                family_id=family.id,
                role="owner"
            )
        )

        await session.commit()
        return family


async def join_family(user_id: int, invite_code: str):
    async with async_session() as session:
        family = await session.scalar(
            select(Family).where(Family.invite_code == invite_code)
        )

        if not family:
            return None

        stmt = (
            insert(family_members)
            .values(
                user_id=user_id,
                family_id=family.id,
                role="member",
            )
            .on_conflict_do_nothing(
                index_elements=["user_id", "family_id"]
            )
        )

        await session.execute(stmt)
        await session.commit()

        return family

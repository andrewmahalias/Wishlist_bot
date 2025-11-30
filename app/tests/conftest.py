import pytest
import pytest_asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, Chat, User as TgUser, Update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database.base import Base
from app.middlewares.auth import AuthMiddleware
from app.middlewares.db import DbSessionMiddleware
from app.handlers.commands import router as start_router
from app.models.models import User


@pytest_asyncio.fixture
async def fsm_context():
    storage = MemoryStorage()
    return FSMContext(storage=storage, key="test_user")


@pytest.fixture
def user():
    return {
        "id": 1,
        "telegram_id": 123456789,
        "name": "John Doe"
    }


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


@pytest_asyncio.fixture
async def session_factory(test_engine):
    return async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest_asyncio.fixture
async def bot():
    return Bot(token="999999:fake-token-for-tests", default=DefaultBotProperties(parse_mode="HTML"))


@pytest_asyncio.fixture
async def dispatcher(session_factory):
    dp = Dispatcher()

    dp.message.middleware(DbSessionMiddleware())
    dp.message.middleware(AuthMiddleware())

    dp.include_router(start_router)

    from app.middlewares.db import SessionLocal as Original
    Original.configure(bind=session_factory.kw['bind'])

    return dp


def make_start_update():
    return Update(
        update_id=1,
        message=Message(
            message_id=1,
            date=12345678,
            chat=Chat(id=123, type="private"),
            text="/start",
            from_user=TgUser(id=777, is_bot=False, first_name="Andrew")
        )
    )


@pytest_asyncio.fixture
async def db_user(session_factory):
    async with session_factory() as session:
        user = User(id=1, telegram_id=777, name="Andrew")
        session.add(user)
        await session.commit()
        return user

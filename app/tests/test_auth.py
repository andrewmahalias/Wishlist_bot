import pytest
from aiogram.methods import SendMessage

from app.models.models import User
from app.tests.conftest import make_start_update


@pytest.mark.asyncio
async def test_user_created(dispatcher, bot, session_factory):
    update = make_start_update()

    sent = []

    async def fake_make_request(bot_, method, timeout=None):
        sent.append(method)
        return {"ok": True, "result": True}

    bot.session.make_request = fake_make_request

    await dispatcher.feed_update(bot, update)

    async with session_factory() as session:
        db_user = await session.get(User, 1)
        assert db_user is not None
        assert db_user.telegram_id == 777
        assert db_user.name == "Andrew"

    assert len(sent) == 1
    assert isinstance(sent[0], SendMessage)
    assert "Привіт" in sent[0].text

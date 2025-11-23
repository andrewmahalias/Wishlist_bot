import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=123)
    return context

@pytest.fixture
def user():
    return {
        "id": 1,
        "telegram_id": 123456789,
        "name": "John Doe"
    }

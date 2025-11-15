import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

@pytest.fixture
def fsm_context():
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=123)
    return context

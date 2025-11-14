import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from app.states.wishlist_states import AddWishState


@pytest.mark.asyncio
async def test_add_wish_state():
    storage = MemoryStorage()
    context = FSMContext(storage=storage, key=123)

    await context.set_state(AddWishState.title)
    state = await context.get_state()
    assert state == AddWishState.title.state

    await context.set_state(AddWishState.description)
    state = await context.get_state()
    assert state == AddWishState.description.state

    await context.set_state(AddWishState.price)
    state = await context.get_state()
    assert state == AddWishState.price.state



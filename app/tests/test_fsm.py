import pytest

from app.states.wishlist_states import AddWishState, DeleteWishState, FamilyViewState, MyWishListState


@pytest.mark.asyncio
async def test_add_wish_state(fsm_context):
    await fsm_context.set_state(AddWishState.title)
    assert await fsm_context.get_state() == AddWishState.title.state

    await fsm_context.set_state(AddWishState.description)
    assert await fsm_context.get_state() == AddWishState.description.state

    await fsm_context.set_state(AddWishState.link)
    assert await fsm_context.get_state() == AddWishState.link.state

    await fsm_context.set_state(AddWishState.price)
    assert await fsm_context.get_state() == AddWishState.price.state

    await fsm_context.set_state(AddWishState.skipping)
    assert await fsm_context.get_state() == AddWishState.skipping.state

    await fsm_context.set_state(AddWishState.canceling)
    assert await fsm_context.get_state() == AddWishState.canceling.state


@pytest.mark.asyncio
async def test_my_wishlist_state(fsm_context):
    await fsm_context.set_state(AddWishState.title)
    assert await fsm_context.get_state() == AddWishState.title.state

    await fsm_context.set_state(MyWishListState.viewing_wishlist)
    assert await fsm_context.get_state() == MyWishListState.viewing_wishlist.state


@pytest.mark.asyncio
async def test_delete_wish_state(fsm_context):
    await fsm_context.set_state(AddWishState.title)
    assert await fsm_context.get_state() == AddWishState.title.state

    await fsm_context.set_state(DeleteWishState.delete)
    assert await fsm_context.get_state() == DeleteWishState.delete.state


@pytest.mark.asyncio
async def test_family_view_state(fsm_context):
    await fsm_context.set_state(AddWishState.title)
    assert await fsm_context.get_state() == AddWishState.title.state

    await fsm_context.set_state(FamilyViewState.selecting_member)
    assert await fsm_context.get_state() == FamilyViewState.selecting_member.state

    await fsm_context.set_state(FamilyViewState.viewing_wishlist)
    assert await fsm_context.get_state() == FamilyViewState.viewing_wishlist.state

    await fsm_context.set_state(FamilyViewState.change_status)
    assert await fsm_context.get_state() == FamilyViewState.change_status.state

from aiogram.fsm.state import StatesGroup, State


class AddWishState(StatesGroup):
    title = State()
    description = State()
    link = State()
    price = State()
    skipping = State()
    canceling = State()


class MyWishListState(StatesGroup):
    viewing_wishlist = State()


class EditWish(StatesGroup):
    title = State()
    description = State()
    link = State()
    price = State()


class DeleteWishState(StatesGroup):
    delete = State()


class FamilyViewState(StatesGroup):
    selecting_member = State()
    viewing_wishlist = State()
    change_status = State()

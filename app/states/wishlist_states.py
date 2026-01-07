from aiogram.fsm.state import StatesGroup, State


class FamilyState(StatesGroup):
    choosing = State()
    creating = State()
    joining = State()


class WishListState(StatesGroup):
    viewing = State()


class AddWishState(StatesGroup):
    title = State()
    description = State()
    link = State()
    price = State()


class EditWishState(StatesGroup):
    title = State()
    description = State()
    link = State()
    price = State()


class DeleteWishState(StatesGroup):
    confirm = State()


class FamilyMemberWishState(StatesGroup):
    selecting_member = State()
    viewing = State()
    change_status = State()


class SupportStates(StatesGroup):
    waiting_for_feedback = State()

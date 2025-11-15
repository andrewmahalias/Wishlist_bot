from aiogram.fsm.state import StatesGroup, State  #todo: check the FSM

class AddWishState(StatesGroup):
    title = State()
    description = State()
    price = State()

class DeleteWishState(StatesGroup):
    selecting = State()

class FamilyViewState(StatesGroup):
    selecting_member = State()
    viewing_wishlist = State()
    change_status = State()


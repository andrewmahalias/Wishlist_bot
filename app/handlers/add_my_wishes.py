from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu
from app.models.models import User, Wish
from app.states.wishlist_states import AddWishState

router = Router()


@router.message(F.text == "➕ Додати бажання")
async def start_add_wish(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AddWishState.title)
    await message.answer(
        "📝 Крок 1/4: Введи назву бажання:",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(AddWishState.title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddWishState.description)
    await message.answer("📝 Крок 2/4: Додай опис:")


@router.message(AddWishState.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddWishState.link)
    await message.answer("🔗 Крок 3/4: Додай посилання:")


@router.message(AddWishState.link)
async def process_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await state.set_state(AddWishState.price)
    await message.answer("💰 Крок 4/4: Вкажи ціну (в грн):")


@router.message(AddWishState.price)
async def process_price(message: Message, state: FSMContext, session: AsyncSession, user: User):
    try:
        price = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer("❌ Введи число:")
        return

    data = await state.get_data()

    wish = Wish(
        user_id=user.id,
        title=data['title'],
        description=data['description'],
        link=data['link'],
        price=price,
        status='active'
    )

    session.add(wish)
    await session.commit()
    await state.clear()
    await message.answer(
        f"✅ Бажання додано!\n\n"
        f"📌 {wish.title}\n"
        f"📝 {wish.description}\n"
        f"🔗 {wish.link}\n"
        f"💰 {wish.price} грн",
        reply_markup=my_wishlist_menu()
    )

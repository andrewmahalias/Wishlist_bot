from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.my_wishlist import my_wishlist_menu, get_wishes_keyboard, get_wishes_details_keyboard
from app.models.models import User, Wish
from app.states.wishlist_states import MyWishListState

router = Router()


@router.message(F.text == "📋 Мої бажання")
async def show_my_wishes(message: Message, session: AsyncSession, user: User, state: FSMContext):
    await state.clear()
    await state.set_state(MyWishListState.viewing_wishlist)
    result = await session.execute(
        select(Wish).where(Wish.user_id == user.id)
    )
    wishes = result.scalars().all()

    if not wishes:
        await message.answer(
            "У тебе ще немає бажань.",
            reply_markup=my_wishlist_menu()
        )
        return

    await message.answer(
        f"📋 <b>Твої бажання ({len(wishes)}):</b>\n"
        "Натисни на бажання:",
        reply_markup=get_wishes_keyboard(wishes)
    )


@router.callback_query(F.data.startswith("wish:"))
async def show_wish_details(callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext):
    """Показати деталі бажання з кнопками Edit/Delete."""
    await state.clear()
    wish_id = int(callback.data.split(":")[1])

    result = await session.execute(
        select(Wish).where(
            Wish.id == wish_id,
            Wish.user_id == user.id
        )
    )
    wish = result.scalar_one_or_none()

    if not wish:
        await callback.answer("Бажання не знайдено", show_alert=True)
        return

    text = f"<b>{wish.title}</b>\n\n"

    if wish.description:
        text += f"📝 {wish.description}\n\n"

    if wish.link:
        text += f"🔗 <a href='{wish.link}'>Перейти за посиланням</a>\n\n"

    if wish.price:
        text += f"💰 €{wish.price}"

    await callback.message.answer(text, reply_markup=get_wishes_details_keyboard(wish), parse_mode="HTML")
    await callback.answer()

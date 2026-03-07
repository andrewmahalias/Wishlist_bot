import html

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.family import get_family_members
from app.crud.user import get_user_by_id
from app.crud.wish import get_user_wishlist
from app.keyboards.my_wishlist import get_wishes_keyboard
from app.models import User, Wish
from app.states.wishlist_states import WishListState

router = Router()


@router.callback_query(F.data.startswith("action:family_wishlist:"))
async def show_family_members(
        cb: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        user: User  # Додаємо user
):
    family_id = int(cb.data.split(":")[-1])
    family_members = await get_family_members(session, family_id)

    # Фільтруємо поточного користувача зі списку
    other_members = [member for member in family_members if member.id != user.id]

    if not other_members:
        await cb.answer("У сім'ї поки немає інших членів 😔", show_alert=True)
        return

    keyboard_buttons = []
    for member in other_members:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"👤 {member.name}",
                callback_data=f"member:wishlist:{member.id}"
            )
        ])

    # Додаємо кнопку "Назад"
    keyboard_buttons.append([
        InlineKeyboardButton(
            text="◀️ Назад",
            callback_data=f"family:select:{family_id}"
        )
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await cb.message.edit_text(
        "Оберіть члена сім'ї:",
        reply_markup=keyboard
    )
    await cb.answer()


@router.callback_query(F.data.startswith("member:wishlist:"))
async def show_member_wishlist(
        cb: CallbackQuery,
        session: AsyncSession,
        state: FSMContext
):
    member_id = int(cb.data.split(":")[-1])

    data = await state.get_data()
    family_id = data.get("family_id")

    wishlist = await get_user_wishlist(
        session,
        user_id=member_id,
        family_id=family_id
    )
    member = await get_user_by_id(session, member_id)

    # Зберігаємо member_id у state для подальшого використання
    await state.update_data(viewing_member_id=member_id)
    await state.set_state(WishListState.viewing_member)

    if not wishlist:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="◀️ Назад до списку",
                callback_data=f"action:family_wishlist:{family_id}"
            )]
        ])
        await cb.message.edit_text(
            f"Wishlist {member.name} порожній 😔",
            reply_markup=keyboard
        )
    else:
        await cb.message.edit_text(
            f"🎁 <b>Wishlist {member.name} ({len(wishlist)}):</b>\nНатисни на бажання:",
            reply_markup=get_wishes_keyboard(wishlist),
            parse_mode="HTML",
        )

    keyboard_builder = InlineKeyboardBuilder.from_markup(
        get_wishes_keyboard(wishlist)
    )
    keyboard_builder.row(
        InlineKeyboardButton(
            text="◀️ Назад до сімʼї",
            callback_data=f"family:select:{family_id}"
        )
    )

    await cb.message.edit_text(
        f"🎁 <b>Wishlist {member.name} ({len(wishlist)}):</b>\nНатисни на бажання:",
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML",
    )

    await cb.answer()


@router.callback_query(
    WishListState.viewing_member,
    F.data.startswith("wish:")
)
async def show_member_wish_details(
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
):
    data = await state.get_data()
    family_id = data.get("family_id")
    member_id = data.get("viewing_member_id")

    if not family_id:
        await callback.answer("Сімʼя не вибрана", show_alert=True)
        return

    try:
        wish_id = int(callback.data.split(":")[1])
    except ValueError:
        await callback.answer("Некоректний ID", show_alert=True)
        return

    result = await session.execute(
        select(Wish).where(
            Wish.id == wish_id,
            Wish.family_id == family_id,
        )
    )
    wish = result.scalar_one_or_none()

    if not wish:
        await callback.answer("Бажання не знайдено", show_alert=True)
        return

    text = f"<b>{html.escape(wish.title)}</b>\n\n"

    if wish.description:
        text += f"📝 {html.escape(wish.description)}\n\n"

    if wish.link:
        text += f"🔗 <a href='{html.escape(wish.link)}'>Посилання</a>\n\n"

    if wish.price is not None:
        text += f"💰 €{html.escape(str(wish.price))}"

    # Кнопка назад до wishlist цього члена сімʼї
    back_button = InlineKeyboardButton(
        text="◀️ Назад до списку",
        callback_data=f"member:wishlist:{member_id}"
    )

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.row(back_button)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard_builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()
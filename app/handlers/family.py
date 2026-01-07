import html

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.family import get_family_by_id
from app.keyboards.done import get_done_keyboard
from app.keyboards.family import families_kb, family_button
from app.models.models import User
from app.services.family_service import (
    get_user_families,
    create_family,
    join_family,
)
from app.states.wishlist_states import FamilyState

router = Router()


@router.message(F.text == "🏠 Сімʼя")
async def family_menu(
        message: Message,
        session: AsyncSession,
        user: User,
):
    families = await get_user_families(session, user.id)

    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        "Оберіть сімʼю:",
        reply_markup=family_reply_kb
    )

    temp = await message.answer(
        "'👇'",
        reply_markup=families_kb(
            [(f.id, f.name) for f in families]
        ),
    )


@router.callback_query(F.data.startswith("family:select:"))
async def select_family(cb: CallbackQuery, state: FSMContext, session: AsyncSession):
    family_id = int(cb.data.split(":")[-1])
    await state.update_data(family_id=family_id)

    # Отримуємо сім'ю з бази
    family = await get_family_by_id(session, family_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📝 Мій wishlist",
                callback_data="action:my_wishlist"
            ),
            InlineKeyboardButton(
                text="🎁 Сімейний wishlist",
                callback_data=f"action:family_wishlist:{family_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔗 Запросити в сім'ю",
                callback_data=f"family:invite:{family_id}"
            )
        ]
    ])

    # Оновлюємо inline меню з назвою сім'ї
    await cb.message.edit_text(
        f"Сім'я «{family.name}» обрана ✅\nОбери дію:",
        reply_markup=keyboard
    )
    await cb.answer()


@router.callback_query(F.data.startswith("family:invite:"))
async def show_invite_code(cb: CallbackQuery, session: AsyncSession, bot):
    family_id = int(cb.data.split(":")[-1])

    family = await get_family_by_id(session, family_id)

    done_kb = get_done_keyboard()

    # Отримуємо username бота
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    # Створюємо deep link
    invite_link = f"https://t.me/{bot_username}?start=join_{family.invite_code}"

    # Екрануємо назву сімʼї
    safe_family_name = html.escape(family.name)

    await cb.message.answer(
        f"🔗 Запрошення в сім'ю «<b>{safe_family_name}</b>»:\n\n"
        f"<b>Код:</b> <code>{family.invite_code}</code>\n\n"
        f"<b>Посилання:</b>\n{invite_link}\n\n"
        f"Поділіться кодом або посиланням з людьми, яких хочете запросити. "
        f"Вони зможуть приєднатись автоматично або через кнопку '🔗 Приєднатись' в меню сімей.",
        parse_mode="HTML",
        reply_markup=done_kb,
        disable_web_page_preview=True
    )
    await cb.answer()


@router.message(F.text == "✅ Готово")
async def done_handler(message: Message, user: User, session: AsyncSession):
    families = await get_user_families(session, user.id)
    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        "Повернення до меню",
        reply_markup=family_reply_kb
    )

    await message.answer(
        "Оберіть сімʼю:",
        reply_markup=families_kb(
            [(f.id, f.name) for f in families]
        )
    )


@router.callback_query(F.data == "family:create")
async def start_create(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.creating)

    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )

    await cb.message.answer(
        "Введіть назву сімʼї:",
        reply_markup=cancel_kb
    )

    await cb.answer()


@router.message(FamilyState.creating, F.text == "❌ Скасувати")
async def cancel_create(message: Message, state: FSMContext, user: User, session: AsyncSession):
    await state.clear()

    # Повертаємо звичайну reply-клавіатуру
    families = await get_user_families(session, user.id)
    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        "Скасовано",
        reply_markup=family_reply_kb
    )

    await message.answer(
        "Оберіть сімʼю:",
        reply_markup=families_kb(
            [(f.id, f.name) for f in families]
        )
    )


@router.message(FamilyState.creating)
async def create_family_handler(
        message: Message,
        state: FSMContext,
        user: User,
        session: AsyncSession,
):
    family = await create_family(session, user.id, message.text.strip())
    await state.clear()

    # Повертаємо звичайну reply-клавіатуру після створення
    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        f"Сімʼю створено ✅\nКод запрошення: `{family.invite_code}`",
        parse_mode="Markdown",
        reply_markup=family_reply_kb
    )


@router.callback_query(F.data == "family:join")
async def start_join(cb: CallbackQuery, state: FSMContext):
    await state.set_state(FamilyState.joining)

    # Оновлюємо reply-клавіатуру на кнопку "Скасувати"
    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )

    await cb.message.answer(
        "Введіть код запрошення:",
        reply_markup=cancel_kb
    )

    await cb.answer()


@router.message(FamilyState.joining, F.text == "❌ Скасувати")
async def cancel_join(message: Message, state: FSMContext, user: User, session: AsyncSession):
    await state.clear()

    # Повертаємо звичайну reply-клавіатуру
    families = await get_user_families(session, user.id)
    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        "Скасовано",
        reply_markup=family_reply_kb
    )

    await message.answer(
        "Оберіть сімʼю:",
        reply_markup=families_kb(
            [(f.id, f.name) for f in families]
        )
    )


@router.message(FamilyState.joining)
async def join_family_handler(
        message: Message,
        state: FSMContext,
        user: User,
        session: AsyncSession,
):
    family = await join_family(session, user.id, message.text.strip().upper())

    if not family:
        await message.answer("Невірний код ❌")
        return

    await state.clear()

    # Повертаємо звичайну reply-клавіатуру після успішного приєднання
    family_reply_kb = ReplyKeyboardMarkup(
        keyboard=family_button(),
        resize_keyboard=True
    )

    await message.answer(
        f"Ви приєднались до сімʼї «{family.name}» ✅",
        reply_markup=family_reply_kb
    )

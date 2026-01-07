import html

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.family import family_button, families_kb
from app.keyboards.start import start_kb
from app.models.models import User
from app.services.family_service import join_family, get_user_families

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_deep_link(
        message: Message,
        session: AsyncSession,
        user: User,
        command: CommandStart,
        state: FSMContext
):
    await state.clear()
    args = command.args

    if args and args.startswith("join_"):
        invite_code = args.replace("join_", "")

        family = await join_family(session, user.id, invite_code)

        if family:

            families = await get_user_families(session, user.id)
            family_reply_kb = ReplyKeyboardMarkup(
                keyboard=family_button(),
                resize_keyboard=True
            )

            safe_family_name = html.escape(family.name)

            await message.answer(
                f"✅ Вітаємо!\n\n"
                f"Ви успішно приєдналися до сімʼї «<b>{safe_family_name}</b>»",
                parse_mode="HTML",
                reply_markup=family_reply_kb
            )

            await message.answer(
                "Оберіть сімʼю:",
                reply_markup=families_kb(
                    [(f.id, f.name) for f in families]
                )
            )
        else:
            # Невірний код або помилка
            await message.answer(
                "❌ Невірний код запрошення або ви вже є членом цієї сімʼї.\n\n"
                "Спробуйте ще раз або зверніться до того, хто надіслав запрошення.",
                reply_markup=start_kb()
            )
    else:
        # Звичайний /start без deep link - показуємо стандартне привітання
        await message.answer(
            f"👋 Привіт, {user.name}!\n\n"
            f"Я допоможу тобі зберігати список бажань.\n"
            f"Натисни на кнопку 'Сімʼя' 🏠 для переходу в меню сімей",
            reply_markup=start_kb()
        )


@router.message(CommandStart())
async def cmd_start(message: Message, user: User, state: FSMContext):
    """Звичайна команда /start (fallback)"""
    await state.clear()
    await message.answer(
        f"👋 Привіт, {user.name}!\n\n"
        f"Я допоможу тобі зберігати список бажань.\n"
        f"Натисни на кнопку 'Сімʼя' 🏠 для переходу в меню сімей",
        reply_markup=start_kb()
    )

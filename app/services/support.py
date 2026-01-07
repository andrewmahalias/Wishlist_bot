from aiogram import Bot
from aiogram.types import Message

ADMIN_ID = 1235586892


async def send_feedback_to_admin(
    bot: Bot,
    message: Message,
):
    user = message.from_user

    text = (
        "📩 <b>Новий фідбек</b>\n\n"
        f"👤 Від: {user.full_name} (@{user.username or '—'})\n"
        f"🆔 ID: {user.id}\n\n"
        f"💬 Повідомлення:\n{message.text}"
    )

    await bot.send_message(
        ADMIN_ID,
        text,
        parse_mode="HTML"
    )

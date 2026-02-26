import html

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_id


async def notify_family_new_wish(
        session: AsyncSession,
        family_id: int,
        author_id: int,
        wish_title: str,
        bot  # передайте bot instance
):
    """Сповіщає всіх членів сім'ї про нове бажання"""

    # Отримуємо всіх членів сім'ї окрім автора
    result = await session.execute(
        select(family_members).where(
            family_members.c.family_id == family_id,
            FamilyMember.user_id != author_id
        )
    )
    family_members = result.scalars().all()

    # Отримуємо ім'я автора
    author = await get_user_by_id(session, author_id)

    # Формуємо повідомлення
    text = (
        f"🔔 <b>Нове бажання в сім'ї!</b>\n\n"
        f"👤 {html.escape(author.name)} додав(ла) бажання:\n"
        f"🎁 <b>{html.escape(wish_title)}</b>\n\n"
        f"Переглянути wishlist можна в меню 👨‍👩‍👧‍👦 Сім'я"
    )

    # Відправляємо повідомлення всім членам
    for member in family_members:
        try:
            await bot.send_message(
                chat_id=member.user_id,
                text=text,
                parse_mode="HTML"
            )
        except Exception as e:
            # Логуємо помилку, але продовжуємо відправку іншим
            print(f"Failed to send notification to user {member.user_id}: {e}")


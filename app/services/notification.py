import html
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, family_members
from app.crud.user import get_user_by_id

logger = logging.getLogger(__name__)


async def notify_family_new_wish(
    session: AsyncSession,
    family_id: int,
    author_id: int,
    wish_title: str,
    bot,
):
    """Notify all family members except the wish author."""

    result = await session.execute(
        select(User).join(
            family_members,
            User.id == family_members.c.user_id,
        ).where(
            family_members.c.family_id == family_id,
            User.id != author_id,
        )
    )

    members = result.scalars().all()

    author = await get_user_by_id(session, author_id)
    author_name = author.name if author else "Хтось"

    logger.info(
        f"Preparing to send wish notification for family_id={family_id} "
        f"from author_id={author_id} to {len(members)} members"
    )

    text = (
        f"🔔 <b>Нове бажання в сім'ї!</b>\n\n"
        f"👤 {html.escape(author_name)} додав(ла) бажання:\n"
        f"🎁 <b>{html.escape(wish_title)}</b>\n\n"
        f"Переглянути wishlist можна в меню 👨‍👩‍👧‍👦 Сім'я"
    )

    success_count = 0
    fail_count = 0

    for member in members:
        try:
            await bot.send_message(
                chat_id=member.telegram_id,
                text=text,
                parse_mode="HTML",
            )
            success_count += 1
            logger.debug(f"Wish notification successfully sent to telegram_id={member.telegram_id}")
        except Exception as e:
            fail_count += 1
            logger.error(
                f"Failed to send notification to "
                f"Telegram user {member.telegram_id}: {e}",
                exc_info=True,
            )

    logger.info(
        f"Wish notification broadcast finished for family_id={family_id}. "
        f"Success: {success_count}, Failed: {fail_count}"
    )
import logging

from aiogram import Bot, Router
from aiogram.types import ChatMemberUpdated

from bot.config import BotConfig
from bot.database.models import upsert_user
from bot.services.subscription import SubscriptionService

logger = logging.getLogger(__name__)

router = Router()


@router.chat_member()
async def on_chat_member_updated(
    event: ChatMemberUpdated,
    bot: Bot,
    config: BotConfig,
    subscription_service: SubscriptionService,
) -> None:
    if event.chat.id != config.channel_id:
        return

    user = event.new_chat_member.user
    if user.is_bot:
        return

    status = event.new_chat_member.status

    await upsert_user(user.id, user.username, user.first_name)
    logger.info(
        "Tracked channel member: %d (@%s) status=%s",
        user.id,
        user.username,
        status,
    )

    if status not in ("member", "administrator", "creator"):
        return

    if status in ("administrator", "creator"):
        return

    if await subscription_service.has_active_subscription(user.id):
        return

    try:
        await bot.ban_chat_member(
            chat_id=config.channel_id,
            user_id=user.id,
        )
        await bot.unban_chat_member(
            chat_id=config.channel_id,
            user_id=user.id,
            only_if_banned=True,
        )
        logger.info(
            "Instant kick non-subscriber %d (@%s) from channel",
            user.id,
            user.username,
        )
    except Exception as e:
        logger.error("Failed to instant kick %d: %s", user.id, e)

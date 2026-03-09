import logging

from aiogram import Router
from aiogram.types import ChatMemberUpdated

from bot.config import BotConfig
from bot.database.models import upsert_user

logger = logging.getLogger(__name__)

router = Router()


@router.chat_member()
async def on_chat_member_updated(event: ChatMemberUpdated, config: BotConfig) -> None:
    if event.chat.id != config.channel_id:
        return

    user = event.new_chat_member.user
    if user.is_bot:
        return

    await upsert_user(user.id, user.username, user.first_name)
    logger.info(
        "Tracked channel member: %d (@%s) status=%s",
        user.id,
        user.username,
        event.new_chat_member.status,
    )

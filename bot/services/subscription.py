import logging
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from bot.config import BotConfig
from bot.database.models import (
    create_subscription,
    deactivate_subscription,
    extend_subscription,
    get_active_subscription,
    upsert_user,
)

logger = logging.getLogger(__name__)


class SubscriptionService:
    def __init__(self, bot: Bot, config: BotConfig) -> None:
        self.bot = bot
        self.config = config

    async def has_active_subscription(self, user_id: int) -> bool:
        sub = await get_active_subscription(user_id)
        if sub is None:
            return False
        expires = datetime.fromisoformat(sub["expires_at"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return expires > datetime.now(UTC)

    async def is_member_of_channel(self, user_id: int) -> bool:
        try:
            member = await self.bot.get_chat_member(
                chat_id=self.config.channel_id,
                user_id=user_id,
            )
            return member.status in ("member", "administrator", "creator")
        except TelegramBadRequest:
            return False

    async def is_admin_of_channel(self, user_id: int) -> bool:
        try:
            member = await self.bot.get_chat_member(
                chat_id=self.config.channel_id,
                user_id=user_id,
            )
            return member.status in ("administrator", "creator")
        except TelegramBadRequest:
            return False

    async def generate_invite_link(self, user_id: int) -> str | None:
        if not await self.has_active_subscription(user_id):
            return None

        if await self.is_member_of_channel(user_id):
            return None

        expire = datetime.now(UTC) + timedelta(hours=24)
        invite = await self.bot.create_chat_invite_link(
            chat_id=self.config.channel_id,
            member_limit=1,
            expire_date=expire,
            name=f"resub_{user_id}",
        )
        logger.info(
            "Re-invite link generated for user %d: %s", user_id, invite.invite_link
        )
        return invite.invite_link

    async def activate_subscription(
        self,
        user_id: int,
        username: str | None,
        first_name: str | None,
        invoice_id: int,
    ) -> tuple[str, bool]:
        await upsert_user(user_id, username, first_name)

        existing = await get_active_subscription(user_id)

        if existing:
            new_expires = await extend_subscription(
                existing["id"], self.config.subscription_days
            )
            logger.info(
                "Subscription extended for user %d until %s",
                user_id,
                new_expires,
            )

            if not await self.is_member_of_channel(user_id):
                expire = datetime.now(UTC) + timedelta(hours=24)
                invite = await self.bot.create_chat_invite_link(
                    chat_id=self.config.channel_id,
                    member_limit=1,
                    expire_date=expire,
                    name=f"renew_{user_id}",
                )
                return invite.invite_link, True

            return "", True

        expire = datetime.now(UTC) + timedelta(hours=24)
        invite = await self.bot.create_chat_invite_link(
            chat_id=self.config.channel_id,
            member_limit=1,
            expire_date=expire,
            name=f"sub_{user_id}",
        )
        invite_link = invite.invite_link

        await create_subscription(
            user_id=user_id,
            invoice_id=invoice_id,
            days=self.config.subscription_days,
            invite_link=invite_link,
        )

        logger.info(
            "Subscription activated for user %d, invite: %s",
            user_id,
            invite_link,
        )
        return invite_link, False

    async def kick_user(self, user_id: int, subscription_id: int) -> None:
        try:
            await self.bot.ban_chat_member(
                chat_id=self.config.channel_id,
                user_id=user_id,
            )
            await self.bot.unban_chat_member(
                chat_id=self.config.channel_id,
                user_id=user_id,
                only_if_banned=True,
            )
            logger.info("Kicked user %d from channel", user_id)
        except Exception as e:
            logger.error("Failed to kick user %d: %s", user_id, e)

        await deactivate_subscription(subscription_id)

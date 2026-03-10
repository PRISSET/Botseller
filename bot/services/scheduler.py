import logging
from datetime import UTC, datetime, timedelta

from aiogram import Bot

from bot.config import BotConfig
from bot.database.models import (
    get_all_known_user_ids,
    get_expired_subscriptions,
    get_reminders_sent,
    get_user_language,
    mark_reminder_sent,
)
from bot.i18n.texts import pluralize_days, t
from bot.keyboards.inline import (
    ICON_BOW,
    ICON_EXPIRED,
    ICON_HOURGLASS,
    ICON_VAMPIRE,
    get_renew_keyboard,
)
from bot.services.subscription import SubscriptionService
from bot.utils import bold, build_caption, cache_gif_id, custom_emoji, get_gif

logger = logging.getLogger(__name__)


async def _get_active_subs_expiring_within(hours: int) -> list[dict]:
    from bot.database.db import get_db

    db = await get_db()
    now = datetime.now(UTC)
    target = now + timedelta(hours=hours)
    cursor = await db.execute(
        """
        SELECT s.*, u.username, u.first_name
        FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.is_active = 1
          AND s.expires_at <= ?
          AND s.expires_at > ?
        """,
        (target.isoformat(), now.isoformat()),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


class SchedulerService:
    def __init__(
        self, bot: Bot, config: BotConfig, subscription_service: SubscriptionService
    ) -> None:
        self.bot = bot
        self.config = config
        self.sub_service = subscription_service

    async def _get_lang(self, user_id: int) -> str:
        lang = await get_user_language(user_id)
        return lang or "ru"

    async def check_subscriptions(self) -> None:
        await self._send_day_reminders()
        await self._send_hour_reminders()
        await self._kick_expired()

    async def _send_reminder_message(
        self, sub: dict, time_text: str, lang: str
    ) -> None:
        price = self.config.subscription_price
        caption, entities = build_caption(
            "    ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("reminder_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("sub_expires_in", lang),
            bold(time_text),
            " ",
            custom_emoji(ICON_HOURGLASS),
            "\n",
            t("renew_to_keep", lang),
            custom_emoji(ICON_VAMPIRE),
        )

        try:
            msg = await self.bot.send_animation(
                chat_id=sub["user_id"],
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_renew_keyboard(price, lang=lang),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)
        except Exception as e:
            logger.error("Failed to send reminder to %d: %s", sub["user_id"], e)
            raise

    async def _send_day_reminders(self) -> None:
        from bot.database.models import get_expiring_subscriptions

        for days in self.config.reminder_days_before:
            subs = await get_expiring_subscriptions(days)
            for sub in subs:
                reminder_key = f"{days}d"
                sent = await get_reminders_sent(sub["id"])
                if reminder_key in sent:
                    continue

                expires = datetime.fromisoformat(sub["expires_at"])
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=UTC)
                days_left = (expires - datetime.now(UTC)).days

                lang = await self._get_lang(sub["user_id"])
                word = pluralize_days(days_left, lang)
                time_text = f"{days_left} {word}"

                try:
                    await self._send_reminder_message(sub, time_text, lang)
                    await mark_reminder_sent(sub["id"], reminder_key)
                    logger.info(
                        "Reminder (%s) sent to user %d", reminder_key, sub["user_id"]
                    )
                except Exception:
                    pass

    async def _send_hour_reminders(self) -> None:
        for hours in self.config.reminder_hours_before:
            subs = await _get_active_subs_expiring_within(hours)
            for sub in subs:
                reminder_key = f"{hours}h"
                sent = await get_reminders_sent(sub["id"])
                if reminder_key in sent:
                    continue

                lang = await self._get_lang(sub["user_id"])
                time_text = t("hour_reminder_text", lang, hours=hours)

                try:
                    await self._send_reminder_message(sub, time_text, lang)
                    await mark_reminder_sent(sub["id"], reminder_key)
                    logger.info(
                        "Reminder (%s) sent to user %d", reminder_key, sub["user_id"]
                    )
                except Exception:
                    pass

    async def _kick_expired(self) -> None:
        price = self.config.subscription_price
        expired = await get_expired_subscriptions()
        for sub in expired:
            lang = await self._get_lang(sub["user_id"])

            caption, entities = build_caption(
                "  ",
                custom_emoji(ICON_BOW),
                " ",
                bold(t("sub_expired_title", lang)),
                " ",
                custom_emoji(ICON_BOW),
                "\n\n",
                t("kicked_from_channel", lang),
                custom_emoji(ICON_EXPIRED),
                "\n",
                t("subscribe_again", lang),
                custom_emoji(ICON_VAMPIRE),
            )
            try:
                msg = await self.bot.send_animation(
                    chat_id=sub["user_id"],
                    animation=await get_gif(),
                    caption=caption,
                    caption_entities=entities,
                    parse_mode=None,
                    reply_markup=get_renew_keyboard(price, lang=lang),
                )
                if msg.animation:
                    cache_gif_id(msg.animation.file_id)
            except Exception as e:
                logger.error("Failed to notify expired user %d: %s", sub["user_id"], e)

            await self.sub_service.kick_user(sub["user_id"], sub["id"])
            logger.info("Kicked expired user %d (sub %d)", sub["user_id"], sub["id"])

    async def check_channel_members(self) -> None:
        await self._kick_non_subscribers()

    async def _kick_non_subscribers(self) -> None:
        user_ids = await get_all_known_user_ids()
        for user_id in user_ids:
            try:
                if not await self.sub_service.is_member_of_channel(user_id):
                    continue

                if await self.sub_service.is_admin_of_channel(user_id):
                    continue

                if await self.sub_service.has_active_subscription(user_id):
                    continue

                await self.bot.ban_chat_member(
                    chat_id=self.config.channel_id,
                    user_id=user_id,
                )
                await self.bot.unban_chat_member(
                    chat_id=self.config.channel_id,
                    user_id=user_id,
                    only_if_banned=True,
                )
                logger.info("Kicked non-subscriber user %d from channel", user_id)
            except Exception as e:
                logger.error("Failed to check/kick non-subscriber %d: %s", user_id, e)

import logging
from datetime import UTC, datetime

from aiogram import Bot

from bot.config import BotConfig
from bot.database.models import (
    get_expired_subscriptions,
    get_expiring_subscriptions,
    mark_reminder_sent,
)
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


class SchedulerService:
    def __init__(
        self, bot: Bot, config: BotConfig, subscription_service: SubscriptionService
    ) -> None:
        self.bot = bot
        self.config = config
        self.sub_service = subscription_service

    async def check_subscriptions(self) -> None:
        await self._send_reminders()
        await self._kick_expired()

    async def _send_reminders(self) -> None:
        price = self.config.subscription_price
        for days in self.config.reminder_days_before:
            subs = await get_expiring_subscriptions(days)
            for sub in subs:
                reminder_col = f"reminder_{days}d"
                if sub.get(reminder_col):
                    continue

                expires = datetime.fromisoformat(sub["expires_at"])
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=UTC)
                days_left = (expires - datetime.now(UTC)).days

                word = (
                    "\u0434\u0435\u043d\u044c"
                    if days_left == 1
                    else "\u0434\u043d\u044f"
                    if 2 <= days_left <= 4
                    else "\u0434\u043d\u0435\u0439"
                )

                caption, entities = build_caption(
                    "    ",
                    custom_emoji(ICON_BOW),
                    " ",
                    bold(
                        "\u041d\u0430\u043f\u043e\u043c\u0438\u043d\u0430\u043d\u0438\u0435"
                    ),
                    " ",
                    custom_emoji(ICON_BOW),
                    "\n\n"
                    "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u0438\u0441\u0442\u0435\u043a\u0430\u0435\u0442 \u0447\u0435\u0440\u0435\u0437 ",
                    bold(f"{days_left} {word}"),
                    " ",
                    custom_emoji(ICON_HOURGLASS),
                    "\n\u041f\u0440\u043e\u0434\u043b\u0438\u0442\u0435, \u0447\u0442\u043e\u0431\u044b \u0441\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0434\u043e\u0441\u0442\u0443\u043f. ",
                    custom_emoji(ICON_VAMPIRE),
                )

                try:
                    msg = await self.bot.send_animation(
                        chat_id=sub["user_id"],
                        animation=await get_gif(),
                        caption=caption,
                        caption_entities=entities,
                        parse_mode=None,
                        reply_markup=get_renew_keyboard(price),
                    )
                    if msg.animation:
                        cache_gif_id(msg.animation.file_id)
                    await mark_reminder_sent(sub["id"], days)
                    logger.info("Reminder (%dd) sent to user %d", days, sub["user_id"])
                except Exception as e:
                    logger.error("Failed to send reminder to %d: %s", sub["user_id"], e)

    async def _kick_expired(self) -> None:
        price = self.config.subscription_price
        expired = await get_expired_subscriptions()
        for sub in expired:
            caption, entities = build_caption(
                "  ",
                custom_emoji(ICON_BOW),
                " ",
                bold(
                    "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u0438\u0441\u0442\u0435\u043a\u043b\u0430"
                ),
                " ",
                custom_emoji(ICON_BOW),
                "\n\n"
                "\u0412\u044b \u0443\u0434\u0430\u043b\u0435\u043d\u044b \u0438\u0437 \u043a\u0430\u043d\u0430\u043b\u0430. ",
                custom_emoji(ICON_EXPIRED),
                "\n\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0437\u0430\u043d\u043e\u0432\u043e \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430. ",
                custom_emoji(ICON_VAMPIRE),
            )
            try:
                msg = await self.bot.send_animation(
                    chat_id=sub["user_id"],
                    animation=await get_gif(),
                    caption=caption,
                    caption_entities=entities,
                    parse_mode=None,
                    reply_markup=get_renew_keyboard(price),
                )
                if msg.animation:
                    cache_gif_id(msg.animation.file_id)
            except Exception as e:
                logger.error("Failed to notify expired user %d: %s", sub["user_id"], e)

            await self.sub_service.kick_user(sub["user_id"], sub["id"])
            logger.info("Kicked expired user %d (sub %d)", sub["user_id"], sub["id"])

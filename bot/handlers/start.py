from datetime import UTC, datetime

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.config import BotConfig
from bot.database.models import get_active_subscription
from bot.keyboards.inline import (
    ICON_ACTIVE,
    ICON_BOW,
    ICON_COIN,
    ICON_EXPIRED,
    ICON_HOURGLASS,
    ICON_STAR,
    ICON_VAMPIRE,
    get_main_keyboard,
)
from bot.services.subscription import SubscriptionService
from bot.utils import bold, build_caption, cache_gif_id, custom_emoji, get_gif

router = Router()


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _now() -> datetime:
    return datetime.now(UTC)


@router.message(CommandStart())
async def cmd_start(message: Message, config: BotConfig) -> None:
    user_id = message.from_user.id
    price = config.subscription_price

    sub = await get_active_subscription(user_id)
    has_sub = False
    if sub:
        expires = _parse_dt(sub["expires_at"])
        if expires > _now():
            has_sub = True

    if has_sub:
        days_left = (expires - _now()).days
        caption, entities = build_caption(
            "    ",
            custom_emoji(ICON_BOW),
            " ",
            bold(
                "\u0421 \u0432\u043e\u0437\u0432\u0440\u0430\u0449\u0435\u043d\u0438\u0435\u043c!"
            ),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430: \u0430\u043a\u0442\u0438\u0432\u043d\u0430 ",
            custom_emoji(ICON_ACTIVE),
            "\n\u041e\u0441\u0442\u0430\u043b\u043e\u0441\u044c: ",
            bold(f"{days_left} \u0434\u043d. "),
            custom_emoji(ICON_HOURGLASS),
        )
        msg = await message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True),
        )
    else:
        caption, entities = build_caption(
            "     ",
            custom_emoji(ICON_BOW),
            " ",
            bold(
                "\u041f\u0440\u0438\u0432\u0430\u0442\u043d\u044b\u0439 \u043a\u0430\u043d\u0430\u043b"
            ),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n\u0426\u0435\u043d\u0430: ",
            bold(f"{price:.0f} USDT / \u043c\u0435\u0441"),
            " ",
            custom_emoji(ICON_COIN),
            "\n\u041e\u0434\u043d\u043e\u0440\u0430\u0437\u043e\u0432\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430-\u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0435\u043d\u0438\u0435 ",
            custom_emoji(ICON_STAR),
            "\n\u041f\u0440\u043e\u0434\u043b\u0435\u043d\u0438\u0435 \u0432 \u043b\u044e\u0431\u043e\u0439 \u043c\u043e\u043c\u0435\u043d\u0442\n\n"
            "\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a \u043a\u0430\u043d\u0430\u043b\u0443. ",
            custom_emoji(ICON_VAMPIRE),
        )
        msg = await message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False),
        )

    if msg.animation:
        cache_gif_id(msg.animation.file_id)


@router.callback_query(F.data == "profile")
async def on_profile(callback: CallbackQuery, config: BotConfig) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = config.subscription_price

    sub = await get_active_subscription(user_id)

    if not sub:
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold("\u041f\u0440\u043e\u0444\u0438\u043b\u044c"),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u0421\u0442\u0430\u0442\u0443\u0441: \u043d\u0435 \u0430\u043a\u0442\u0438\u0432\u043d\u0430 ",
            custom_emoji(ICON_EXPIRED),
            "\n\n"
            "\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0434\u043b\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430 \u043a \u043a\u0430\u043d\u0430\u043b\u0443. ",
            custom_emoji(ICON_VAMPIRE),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    expires = _parse_dt(sub["expires_at"])
    now = _now()
    delta = expires - now
    days_left = delta.days
    hours_left = int(delta.total_seconds() // 3600) % 24
    active = expires > now

    if active:
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold("\u041f\u0440\u043e\u0444\u0438\u043b\u044c"),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u0421\u0442\u0430\u0442\u0443\u0441: \u0430\u043a\u0442\u0438\u0432\u043d\u0430 ",
            custom_emoji(ICON_ACTIVE),
            "\n\u0418\u0441\u0442\u0435\u043a\u0430\u0435\u0442: ",
            bold(expires.strftime("%d.%m.%Y %H:%M")),
            "\n\u041e\u0441\u0442\u0430\u043b\u043e\u0441\u044c: ",
            bold(f"{days_left} \u0434\u043d. {hours_left} \u0447. "),
            custom_emoji(ICON_HOURGLASS),
            "\n\n\u041f\u0440\u043e\u0434\u043b\u0435\u043d\u0438\u0435 \u0434\u043e\u0431\u0430\u0432\u043b\u044f\u0435\u0442 ",
            bold("+30 \u0434\u043d\u0435\u0439"),
        )
    else:
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold("\u041f\u0440\u043e\u0444\u0438\u043b\u044c"),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u0421\u0442\u0430\u0442\u0443\u0441: \u043d\u0435 \u0430\u043a\u0442\u0438\u0432\u043d\u0430 ",
            custom_emoji(ICON_EXPIRED),
            "\n\u0418\u0441\u0442\u0435\u043a\u043b\u0430: ",
            bold(expires.strftime("%d.%m.%Y %H:%M")),
            "\n\n\u041e\u0444\u043e\u0440\u043c\u0438\u0442\u0435 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0443 \u0434\u043b\u044f \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f \u0434\u043e\u0441\u0442\u0443\u043f\u0430. ",
            custom_emoji(ICON_VAMPIRE),
        )

    msg = await callback.message.answer_animation(
        animation=await get_gif(),
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=get_main_keyboard(price, has_subscription=active),
    )
    if msg.animation:
        cache_gif_id(msg.animation.file_id)


@router.callback_query(F.data == "get_invite_link")
async def on_get_invite_link(
    callback: CallbackQuery,
    bot: Bot,
    config: BotConfig,
    subscription_service: SubscriptionService,
) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = config.subscription_price

    if not await subscription_service.has_active_subscription(user_id):
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold("\u041e\u0448\u0438\u0431\u043a\u0430"),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u0423 \u0432\u0430\u0441 \u043d\u0435\u0442 \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0439 \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0438. ",
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    if await subscription_service.is_member_of_channel(user_id):
        caption, entities = build_caption(
            "   ",
            custom_emoji(ICON_BOW),
            " ",
            bold(
                "\u0412\u044b \u0443\u0436\u0435 \u0432 \u043a\u0430\u043d\u0430\u043b\u0435"
            ),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u041d\u043e\u0432\u0430\u044f \u0441\u0441\u044b\u043b\u043a\u0430 \u043d\u0435 \u0442\u0440\u0435\u0431\u0443\u0435\u0442\u0441\u044f. ",
            custom_emoji(ICON_ACTIVE),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    invite_link = await subscription_service.generate_invite_link(user_id)
    if invite_link:
        caption, entities = build_caption(
            " ",
            custom_emoji(ICON_BOW),
            " ",
            bold(
                "\u0421\u0441\u044b\u043b\u043a\u0430-\u043f\u0440\u0438\u0433\u043b\u0430\u0448\u0435\u043d\u0438\u0435"
            ),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n"
            "\u0412\u0430\u0448\u0430 \u0441\u0441\u044b\u043b\u043a\u0430 (\u043e\u0434\u043d\u043e\u0440\u0430\u0437\u043e\u0432\u0430\u044f):\n"
            f"{invite_link} ",
            custom_emoji(ICON_STAR),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True),
        )
    else:
        caption, entities = build_caption(
            "\u041e\u0448\u0438\u0431\u043a\u0430 \u0433\u0435\u043d\u0435\u0440\u0430\u0446\u0438\u0438 \u0441\u0441\u044b\u043b\u043a\u0438. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435. ",
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True),
        )
    if msg.animation:
        cache_gif_id(msg.animation.file_id)

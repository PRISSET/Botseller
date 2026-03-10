from datetime import UTC, datetime

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from bot.config import BotConfig
from bot.database.models import get_active_subscription, set_user_language
from bot.i18n.texts import t
from bot.keyboards.inline import (
    ICON_ACTIVE,
    ICON_BOW,
    ICON_COIN,
    ICON_EXPIRED,
    ICON_HOURGLASS,
    ICON_RENEW_STAR,
    ICON_STAR,
    ICON_VAMPIRE,
    get_language_keyboard,
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


async def _send_main_menu(message: Message, config: BotConfig, lang: str) -> None:
    user_id = message.from_user.id
    price = config.subscription_price

    sub = await get_active_subscription(user_id)
    has_sub = False
    expires = None
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
            bold(t("welcome_back", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("sub_active", lang),
            custom_emoji(ICON_ACTIVE),
            "\n",
            t("remaining", lang),
            bold(t("days_left", lang, days=days_left)),
            custom_emoji(ICON_HOURGLASS),
        )
        msg = await message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True, lang=lang),
        )
    else:
        caption, entities = build_caption(
            "     ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("private_channel", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("price_line", lang),
            bold(t("price_value", lang, price=f"{price:.0f}")),
            " ",
            custom_emoji(ICON_COIN),
            "\n",
            t("one_time_link", lang),
            custom_emoji(ICON_STAR),
            "\n",
            t("renew_anytime", lang),
            custom_emoji(ICON_RENEW_STAR),
            "\n\n",
            t("subscribe_cta", lang),
            custom_emoji(ICON_VAMPIRE),
        )
        msg = await message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False, lang=lang),
        )

    if msg.animation:
        cache_gif_id(msg.animation.file_id)


@router.message(CommandStart())
async def cmd_start(
    message: Message, config: BotConfig, lang: str, has_language: bool
) -> None:
    if not has_language:
        await message.answer(
            t("choose_language", "ru"),
            reply_markup=get_language_keyboard(),
        )
        return

    await _send_main_menu(message, config, lang)


@router.callback_query(F.data.startswith("set_lang:"))
async def on_set_language(callback: CallbackQuery, config: BotConfig) -> None:
    await callback.answer()
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id

    await set_user_language(user_id, lang)

    await callback.message.answer(t("language_set", lang))
    await _send_main_menu(callback.message, config, lang)


@router.callback_query(F.data == "change_language")
async def on_change_language(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        t("choose_language", "ru"),
        reply_markup=get_language_keyboard(),
    )


@router.callback_query(F.data == "profile")
async def on_profile(callback: CallbackQuery, config: BotConfig, lang: str) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = config.subscription_price

    sub = await get_active_subscription(user_id)

    if not sub:
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("profile_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("status_inactive", lang),
            custom_emoji(ICON_EXPIRED),
            "\n\n",
            t("subscribe_for_access", lang),
            custom_emoji(ICON_VAMPIRE),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False, lang=lang),
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
            bold(t("profile_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("status_active", lang),
            custom_emoji(ICON_ACTIVE),
            "\n",
            t("expires_label", lang),
            bold(expires.strftime("%d.%m.%Y %H:%M")),
            "\n",
            t("remaining", lang),
            bold(t("remaining_detail", lang, days=days_left, hours=hours_left)),
            custom_emoji(ICON_HOURGLASS),
            "\n\n",
            t("renew_adds", lang),
            bold(t("plus_30_days", lang)),
        )
    else:
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("profile_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("status_expired_label", lang),
            custom_emoji(ICON_EXPIRED),
            "\n",
            t("expired_at", lang),
            bold(expires.strftime("%d.%m.%Y %H:%M")),
            "\n\n",
            t("subscribe_to_restore", lang),
            custom_emoji(ICON_VAMPIRE),
        )

    msg = await callback.message.answer_animation(
        animation=await get_gif(),
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=get_main_keyboard(price, has_subscription=active, lang=lang),
    )
    if msg.animation:
        cache_gif_id(msg.animation.file_id)


@router.callback_query(F.data == "get_invite_link")
async def on_get_invite_link(
    callback: CallbackQuery,
    bot: Bot,
    config: BotConfig,
    subscription_service: SubscriptionService,
    lang: str,
) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = config.subscription_price

    if not await subscription_service.has_active_subscription(user_id):
        caption, entities = build_caption(
            "          ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("error_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("no_active_sub", lang),
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=False, lang=lang),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    if await subscription_service.is_member_of_channel(user_id):
        caption, entities = build_caption(
            "   ",
            custom_emoji(ICON_BOW),
            " ",
            bold(t("already_in_channel", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("no_link_needed", lang),
            custom_emoji(ICON_ACTIVE),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True, lang=lang),
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
            bold(t("invite_link_title", lang)),
            " ",
            custom_emoji(ICON_BOW),
            "\n\n",
            t("your_link", lang),
            f"{invite_link} ",
            custom_emoji(ICON_STAR),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True, lang=lang),
        )
    else:
        caption, entities = build_caption(
            t("link_gen_error", lang),
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_subscription=True, lang=lang),
        )
    if msg.animation:
        cache_gif_id(msg.animation.file_id)

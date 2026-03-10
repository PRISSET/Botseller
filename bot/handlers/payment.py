import json
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.config import BotConfig
from bot.database.models import get_active_subscription
from bot.i18n.texts import t
from bot.keyboards.inline import (
    ICON_ACTIVE,
    ICON_BOW,
    ICON_COIN,
    ICON_EXPIRED,
    ICON_HOURGLASS,
    ICON_STAR,
    get_main_keyboard,
    get_payment_keyboard,
)
from bot.services.crypto_pay import CryptoPayService
from bot.services.subscription import SubscriptionService
from bot.utils import bold, build_caption, cache_gif_id, custom_emoji, get_gif

logger = logging.getLogger(__name__)

router = Router()

_pending_invoices: dict[int, dict] = {}


@router.callback_query(F.data == "buy_subscription")
async def on_buy_subscription(
    callback: CallbackQuery,
    bot: Bot,
    config: BotConfig,
    crypto_pay: CryptoPayService,
    subscription_service: SubscriptionService,
    lang: str,
) -> None:
    await callback.answer()
    user_id = callback.from_user.id
    price = config.subscription_price

    payload = json.dumps({"user_id": user_id})
    try:
        invoice = await crypto_pay.create_invoice(
            amount=price,
            currency="USDT",
            description=f"Subscription 1 month - {user_id}",
            payload=payload,
        )
    except Exception as e:
        logger.error("Failed to create invoice for user %d: %s", user_id, e)
        caption, entities = build_caption(
            t("invoice_create_error", lang),
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    _pending_invoices[user_id] = invoice
    has_sub = await subscription_service.has_active_subscription(user_id)
    action = t("type_renewal", lang) if has_sub else t("type_new_sub", lang)

    caption, entities = build_caption(
        "    ",
        custom_emoji(ICON_BOW),
        " ",
        bold(t("invoice_title", lang)),
        " ",
        custom_emoji(ICON_BOW),
        "\n\n",
        t("type_label", lang),
        bold(action),
        "\n",
        t("amount_label", lang),
        bold(f"{price} USDT"),
        " ",
        custom_emoji(ICON_COIN),
        "\n",
        t("period_label", lang),
        bold(t("plus_30_days", lang)),
        " ",
        custom_emoji(ICON_HOURGLASS),
        "\n\n",
        t("step_1", lang),
        bold(t("step_1_action", lang)),
        "\n",
        t("step_2", lang),
        bold(t("step_2_action", lang)),
    )
    msg = await callback.message.answer_animation(
        animation=await get_gif(),
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=get_payment_keyboard(invoice["pay_url"], lang=lang),
    )
    if msg.animation:
        cache_gif_id(msg.animation.file_id)


@router.callback_query(F.data == "check_payment")
async def on_check_payment(
    callback: CallbackQuery,
    bot: Bot,
    config: BotConfig,
    crypto_pay: CryptoPayService,
    subscription_service: SubscriptionService,
    lang: str,
) -> None:
    await callback.answer(t("checking", lang))
    user_id = callback.from_user.id
    price = config.subscription_price

    invoice = _pending_invoices.get(user_id)
    if not invoice:
        has_sub = await subscription_service.has_active_subscription(user_id)
        caption, entities = build_caption(
            t("no_active_invoice", lang),
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_sub, lang=lang),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)
        return

    try:
        invoices_data = await crypto_pay.get_invoices(
            invoice_ids=str(invoice["invoice_id"])
        )

        items = (
            invoices_data
            if isinstance(invoices_data, list)
            else invoices_data.get("items", [])
        )
        if not items:
            caption, entities = build_caption(
                t("payment_not_found", lang),
                custom_emoji(ICON_EXPIRED),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_payment_keyboard(invoice["pay_url"], lang=lang),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)
            return

        current_invoice = items[0] if isinstance(items, list) else items
        status = current_invoice.get("status")

        if status == "paid":
            _pending_invoices.pop(user_id, None)

            invite_link, is_renewal = await subscription_service.activate_subscription(
                user_id=user_id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                invoice_id=invoice["invoice_id"],
            )

            if is_renewal:
                sub = await get_active_subscription(user_id)
                new_expires = datetime.fromisoformat(sub["expires_at"]) if sub else None
                expires_str = (
                    new_expires.strftime("%d.%m.%Y %H:%M") if new_expires else "N/A"
                )
                segments: list[dict | str] = [
                    "  ",
                    custom_emoji(ICON_BOW),
                    " ",
                    bold(t("sub_extended", lang)),
                    " ",
                    custom_emoji(ICON_BOW),
                    "\n\n",
                    t("valid_until", lang),
                    bold(expires_str),
                    " ",
                    custom_emoji(ICON_HOURGLASS),
                ]
                if invite_link:
                    segments.extend(
                        [
                            "\n\n",
                            t("entry_link", lang),
                            f"{invite_link} ",
                            custom_emoji(ICON_STAR),
                        ]
                    )
                caption, entities = build_caption(*segments)
                msg = await callback.message.answer_animation(
                    animation=await get_gif(),
                    caption=caption,
                    caption_entities=entities,
                    parse_mode=None,
                    reply_markup=get_main_keyboard(
                        price, has_subscription=True, lang=lang
                    ),
                )
            else:
                caption, entities = build_caption(
                    "    ",
                    custom_emoji(ICON_BOW),
                    " ",
                    bold(t("payment_received", lang)),
                    " ",
                    custom_emoji(ICON_BOW),
                    "\n\n",
                    t("your_link_onetime", lang),
                    f"{invite_link} ",
                    custom_emoji(ICON_STAR),
                    "\n\n",
                    t("sub_label", lang),
                    bold(t("thirty_days", lang)),
                    " ",
                    custom_emoji(ICON_ACTIVE),
                )
                msg = await callback.message.answer_animation(
                    animation=await get_gif(),
                    caption=caption,
                    caption_entities=entities,
                    parse_mode=None,
                    reply_markup=get_main_keyboard(
                        price, has_subscription=True, lang=lang
                    ),
                )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)

        elif status == "expired":
            _pending_invoices.pop(user_id, None)
            has_sub = await subscription_service.has_active_subscription(user_id)
            caption, entities = build_caption(
                t("payment_expired", lang),
                custom_emoji(ICON_EXPIRED),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_main_keyboard(price, has_sub, lang=lang),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)
        else:
            caption, entities = build_caption(
                t("payment_pending", lang),
                custom_emoji(ICON_HOURGLASS),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_payment_keyboard(invoice["pay_url"], lang=lang),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)

    except Exception as e:
        logger.error("Failed to check payment for user %d: %s", user_id, e)
        caption, entities = build_caption(
            t("check_error", lang),
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_payment_keyboard(invoice["pay_url"], lang=lang),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)

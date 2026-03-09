import json
import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from bot.config import BotConfig
from bot.database.models import get_active_subscription
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
            "\u041e\u0448\u0438\u0431\u043a\u0430 \u0441\u043e\u0437\u0434\u0430\u043d\u0438\u044f \u0441\u0447\u0451\u0442\u0430. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435. ",
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
    action = (
        "\u041f\u0440\u043e\u0434\u043b\u0435\u043d\u0438\u0435"
        if has_sub
        else "\u041d\u043e\u0432\u0430\u044f \u043f\u043e\u0434\u043f\u0438\u0441\u043a\u0430"
    )

    caption, entities = build_caption(
        "    ",
        custom_emoji(ICON_BOW),
        " ",
        bold(
            "\u0421\u0447\u0451\u0442 \u043d\u0430 \u043e\u043f\u043b\u0430\u0442\u0443"
        ),
        " ",
        custom_emoji(ICON_BOW),
        "\n\n\u0422\u0438\u043f: ",
        bold(action),
        "\n\u0421\u0443\u043c\u043c\u0430: ",
        bold(f"{price} USDT"),
        " ",
        custom_emoji(ICON_COIN),
        "\n\u0421\u0440\u043e\u043a: ",
        bold("+30 \u0434\u043d\u0435\u0439"),
        " ",
        custom_emoji(ICON_HOURGLASS),
        "\n\n1. \u041d\u0430\u0436\u043c\u0438\u0442\u0435 ",
        bold("\u041e\u043f\u043b\u0430\u0442\u0438\u0442\u044c"),
        "\n2. \u041d\u0430\u0436\u043c\u0438\u0442\u0435 ",
        bold(
            "\u041f\u0440\u043e\u0432\u0435\u0440\u0438\u0442\u044c \u043e\u043f\u043b\u0430\u0442\u0443"
        ),
    )
    msg = await callback.message.answer_animation(
        animation=await get_gif(),
        caption=caption,
        caption_entities=entities,
        parse_mode=None,
        reply_markup=get_payment_keyboard(invoice["pay_url"]),
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
) -> None:
    await callback.answer("\u041f\u0440\u043e\u0432\u0435\u0440\u044f\u044e...")
    user_id = callback.from_user.id
    price = config.subscription_price

    invoice = _pending_invoices.get(user_id)
    if not invoice:
        has_sub = await subscription_service.has_active_subscription(user_id)
        caption, entities = build_caption(
            "\u041d\u0435\u0442 \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0433\u043e \u0441\u0447\u0451\u0442\u0430. ",
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_main_keyboard(price, has_sub),
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
                "\u041e\u043f\u043b\u0430\u0442\u0430 \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u0430. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435. ",
                custom_emoji(ICON_EXPIRED),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_payment_keyboard(invoice["pay_url"]),
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
                    bold(
                        "\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430 \u043f\u0440\u043e\u0434\u043b\u0435\u043d\u0430!"
                    ),
                    " ",
                    custom_emoji(ICON_BOW),
                    "\n\n"
                    "\u0414\u0435\u0439\u0441\u0442\u0432\u0443\u0435\u0442 \u0434\u043e: ",
                    bold(expires_str),
                    " ",
                    custom_emoji(ICON_HOURGLASS),
                ]
                if invite_link:
                    segments.extend(
                        [
                            "\n\n\u0421\u0441\u044b\u043b\u043a\u0430 \u0434\u043b\u044f \u0432\u0445\u043e\u0434\u0430:\n"
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
                    reply_markup=get_main_keyboard(price, has_subscription=True),
                )
            else:
                caption, entities = build_caption(
                    "    ",
                    custom_emoji(ICON_BOW),
                    " ",
                    bold(
                        "\u041e\u043f\u043b\u0430\u0442\u0430 \u043f\u043e\u043b\u0443\u0447\u0435\u043d\u0430!"
                    ),
                    " ",
                    custom_emoji(ICON_BOW),
                    "\n\n"
                    "\u0412\u0430\u0448\u0430 \u0441\u0441\u044b\u043b\u043a\u0430 (\u043e\u0434\u043d\u043e\u0440\u0430\u0437\u043e\u0432\u0430\u044f):\n"
                    f"{invite_link} ",
                    custom_emoji(ICON_STAR),
                    "\n\n\u041f\u043e\u0434\u043f\u0438\u0441\u043a\u0430: ",
                    bold("30 \u0434\u043d\u0435\u0439"),
                    " ",
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

        elif status == "expired":
            _pending_invoices.pop(user_id, None)
            has_sub = await subscription_service.has_active_subscription(user_id)
            caption, entities = build_caption(
                "\u0412\u0440\u0435\u043c\u044f \u043e\u043f\u043b\u0430\u0442\u044b \u0438\u0441\u0442\u0435\u043a\u043b\u043e. \u0421\u043e\u0437\u0434\u0430\u0439\u0442\u0435 \u043d\u043e\u0432\u044b\u0439 \u0441\u0447\u0451\u0442. ",
                custom_emoji(ICON_EXPIRED),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_main_keyboard(price, has_sub),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)
        else:
            caption, entities = build_caption(
                "\u041e\u043f\u043b\u0430\u0442\u0430 \u0435\u0449\u0451 \u043d\u0435 \u043f\u043e\u0441\u0442\u0443\u043f\u0438\u043b\u0430. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435. ",
                custom_emoji(ICON_HOURGLASS),
            )
            msg = await callback.message.answer_animation(
                animation=await get_gif(),
                caption=caption,
                caption_entities=entities,
                parse_mode=None,
                reply_markup=get_payment_keyboard(invoice["pay_url"]),
            )
            if msg.animation:
                cache_gif_id(msg.animation.file_id)

    except Exception as e:
        logger.error("Failed to check payment for user %d: %s", user_id, e)
        caption, entities = build_caption(
            "\u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u043e\u0432\u0435\u0440\u043a\u0438. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u043f\u043e\u0437\u0436\u0435. ",
            custom_emoji(ICON_EXPIRED),
        )
        msg = await callback.message.answer_animation(
            animation=await get_gif(),
            caption=caption,
            caption_entities=entities,
            parse_mode=None,
            reply_markup=get_payment_keyboard(invoice["pay_url"]),
        )
        if msg.animation:
            cache_gif_id(msg.animation.file_id)

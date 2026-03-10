from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.i18n.texts import t

ICON_STAR = "5283084720706452500"
ICON_COIN = "5345824065368128623"
ICON_ACTIVE = "5346019086948138250"
ICON_EXPIRED = "5345871468922174077"
ICON_HOURGLASS = "5346220920346277355"
ICON_BOW = "5465292751119609438"
ICON_VAMPIRE = "5467458484083640673"


def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="\U0001f1f7\U0001f1fa Русский",
                    callback_data="set_lang:ru",
                ),
                InlineKeyboardButton(
                    text="\U0001f1ec\U0001f1e7 English",
                    callback_data="set_lang:en",
                ),
            ]
        ]
    )


def get_main_keyboard(
    price: float, has_subscription: bool = False, lang: str = "ru"
) -> InlineKeyboardMarkup:
    buttons = []

    profile_icon = ICON_ACTIVE if has_subscription else ICON_EXPIRED
    buttons.append(
        [
            InlineKeyboardButton(
                text=t("btn_profile", lang),
                callback_data="profile",
                icon_custom_emoji_id=profile_icon,
            )
        ]
    )

    if has_subscription:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t("btn_renew", lang, price=f"{price:.0f}"),
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t("btn_get_link", lang),
                    callback_data="get_invite_link",
                    icon_custom_emoji_id=ICON_STAR,
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=t("btn_subscribe", lang, price=f"{price:.0f}"),
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text=t("btn_change_lang", lang),
                callback_data="change_language",
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_keyboard(pay_url: str, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_pay", lang),
                    url=pay_url,
                    icon_custom_emoji_id=ICON_COIN,
                )
            ],
            [
                InlineKeyboardButton(
                    text=t("btn_check_payment", lang),
                    callback_data="check_payment",
                    icon_custom_emoji_id=ICON_STAR,
                )
            ],
        ]
    )


def get_renew_keyboard(price: float, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("btn_renew", lang, price=f"{price:.0f}"),
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        ]
    )

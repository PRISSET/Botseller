from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ICON_STAR = "5283084720706452500"
ICON_COIN = "5345824065368128623"
ICON_ACTIVE = "5346019086948138250"
ICON_EXPIRED = "5345871468922174077"
ICON_HOURGLASS = "5346220920346277355"
ICON_BOW = "5465292751119609438"
ICON_VAMPIRE = "5467458484083640673"


def get_main_keyboard(
    price: float, has_subscription: bool = False
) -> InlineKeyboardMarkup:
    buttons = []

    profile_icon = ICON_ACTIVE if has_subscription else ICON_EXPIRED
    buttons.append(
        [
            InlineKeyboardButton(
                text="Профиль",
                callback_data="profile",
                icon_custom_emoji_id=profile_icon,
            )
        ]
    )

    if has_subscription:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Продлить  ${price:.0f}/мес",
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        )
        buttons.append(
            [
                InlineKeyboardButton(
                    text="Получить ссылку",
                    callback_data="get_invite_link",
                    icon_custom_emoji_id=ICON_STAR,
                )
            ]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"Подписаться  ${price:.0f}/мес",
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_keyboard(pay_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Оплатить",
                    url=pay_url,
                    icon_custom_emoji_id=ICON_COIN,
                )
            ],
            [
                InlineKeyboardButton(
                    text="Проверить оплату",
                    callback_data="check_payment",
                    icon_custom_emoji_id=ICON_STAR,
                )
            ],
        ]
    )


def get_renew_keyboard(price: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Продлить  ${price:.0f}/мес",
                    callback_data="buy_subscription",
                    icon_custom_emoji_id=ICON_COIN,
                )
            ]
        ]
    )

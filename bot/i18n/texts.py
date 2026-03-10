from typing import Any

TEXTS: dict[str, dict[str, str]] = {
    "choose_language": {
        "ru": "\U0001f30d Выберите язык / Choose language:",
        "en": "\U0001f30d Choose language / Выберите язык:",
    },
    "language_set": {
        "ru": "Язык установлен: Русский \U0001f1f7\U0001f1fa",
        "en": "Language set: English \U0001f1ec\U0001f1e7",
    },
    "btn_lang_ru": {
        "ru": "\U0001f1f7\U0001f1fa Русский",
        "en": "\U0001f1f7\U0001f1fa Русский",
    },
    "btn_lang_en": {
        "ru": "\U0001f1ec\U0001f1e7 English",
        "en": "\U0001f1ec\U0001f1e7 English",
    },
    "btn_profile": {
        "ru": "Профиль",
        "en": "Profile",
    },
    "btn_subscribe": {
        "ru": "Подписаться  ${price}/мес",
        "en": "Subscribe  ${price}/mo",
    },
    "btn_renew": {
        "ru": "Продлить  ${price}/мес",
        "en": "Renew  ${price}/mo",
    },
    "btn_get_link": {
        "ru": "Получить ссылку",
        "en": "Get invite link",
    },
    "btn_pay": {
        "ru": "Оплатить",
        "en": "Pay",
    },
    "btn_check_payment": {
        "ru": "Проверить оплату",
        "en": "Check payment",
    },
    "btn_change_lang": {
        "ru": "\U0001f1ec\U0001f1e7 English",
        "en": "\U0001f1f7\U0001f1fa Русский",
    },
    "welcome_back": {
        "ru": "С возвращением!",
        "en": "Welcome back!",
    },
    "sub_active": {
        "ru": "Подписка: активна ",
        "en": "Subscription: active ",
    },
    "days_left": {
        "ru": "{days} дн. ",
        "en": "{days} days ",
    },
    "remaining": {
        "ru": "Осталось: ",
        "en": "Remaining: ",
    },
    "private_channel": {
        "ru": "Приватный канал",
        "en": "Private channel",
    },
    "price_line": {
        "ru": "Цена: ",
        "en": "Price: ",
    },
    "price_value": {
        "ru": "{price} USDT / мес",
        "en": "{price} USDT / mo",
    },
    "one_time_link": {
        "ru": "Одноразовая ссылка-приглашение ",
        "en": "One-time invite link ",
    },
    "renew_anytime": {
        "ru": "Продление в любой момент ",
        "en": "Renew anytime ",
    },
    "subscribe_cta": {
        "ru": "Оформите подписку для доступа к каналу. ",
        "en": "Subscribe to access the channel. ",
    },
    "profile_title": {
        "ru": "Профиль",
        "en": "Profile",
    },
    "status_inactive": {
        "ru": "Статус: не активна ",
        "en": "Status: inactive ",
    },
    "subscribe_for_access": {
        "ru": "Оформите подписку для доступа к каналу. ",
        "en": "Subscribe to access the channel. ",
    },
    "status_active": {
        "ru": "Статус: активна ",
        "en": "Status: active ",
    },
    "expires_label": {
        "ru": "Истекает: ",
        "en": "Expires: ",
    },
    "remaining_detail": {
        "ru": "{days} дн. {hours} ч. ",
        "en": "{days}d {hours}h ",
    },
    "renew_adds": {
        "ru": "Продление добавляет ",
        "en": "Renewal adds ",
    },
    "plus_30_days": {
        "ru": "+30 дней",
        "en": "+30 days",
    },
    "status_expired_label": {
        "ru": "Статус: не активна ",
        "en": "Status: inactive ",
    },
    "expired_at": {
        "ru": "Истекла: ",
        "en": "Expired: ",
    },
    "subscribe_to_restore": {
        "ru": "Оформите подписку для восстановления доступа. ",
        "en": "Subscribe to restore access. ",
    },
    "error_title": {
        "ru": "Ошибка",
        "en": "Error",
    },
    "no_active_sub": {
        "ru": "У вас нет активной подписки. ",
        "en": "You have no active subscription. ",
    },
    "already_in_channel": {
        "ru": "Вы уже в канале",
        "en": "Already in channel",
    },
    "no_link_needed": {
        "ru": "Новая ссылка не требуется. ",
        "en": "No new link needed. ",
    },
    "invite_link_title": {
        "ru": "Ссылка-приглашение",
        "en": "Invite link",
    },
    "your_link": {
        "ru": "Ваша ссылка (одноразовая):\n",
        "en": "Your link (one-time):\n",
    },
    "link_gen_error": {
        "ru": "Ошибка генерации ссылки. Попробуйте позже. ",
        "en": "Link generation failed. Try again later. ",
    },
    "invoice_create_error": {
        "ru": "Ошибка создания счёта. Попробуйте позже. ",
        "en": "Invoice creation failed. Try again later. ",
    },
    "invoice_title": {
        "ru": "Счёт на оплату",
        "en": "Payment invoice",
    },
    "type_label": {
        "ru": "Тип: ",
        "en": "Type: ",
    },
    "type_renewal": {
        "ru": "Продление",
        "en": "Renewal",
    },
    "type_new_sub": {
        "ru": "Новая подписка",
        "en": "New subscription",
    },
    "amount_label": {
        "ru": "Сумма: ",
        "en": "Amount: ",
    },
    "period_label": {
        "ru": "Срок: ",
        "en": "Period: ",
    },
    "step_1": {
        "ru": "1. Нажмите ",
        "en": "1. Press ",
    },
    "step_1_action": {
        "ru": "Оплатить",
        "en": "Pay",
    },
    "step_2": {
        "ru": "2. Нажмите ",
        "en": "2. Press ",
    },
    "step_2_action": {
        "ru": "Проверить оплату",
        "en": "Check payment",
    },
    "checking": {
        "ru": "Проверяю...",
        "en": "Checking...",
    },
    "no_active_invoice": {
        "ru": "Нет активного счёта. ",
        "en": "No active invoice. ",
    },
    "payment_not_found": {
        "ru": "Оплата не найдена. Попробуйте позже. ",
        "en": "Payment not found. Try again later. ",
    },
    "sub_extended": {
        "ru": "Подписка продлена!",
        "en": "Subscription renewed!",
    },
    "valid_until": {
        "ru": "Действует до: ",
        "en": "Valid until: ",
    },
    "entry_link": {
        "ru": "Ссылка для входа:\n",
        "en": "Entry link:\n",
    },
    "payment_received": {
        "ru": "Оплата получена!",
        "en": "Payment received!",
    },
    "your_link_onetime": {
        "ru": "Ваша ссылка (одноразовая):\n",
        "en": "Your link (one-time):\n",
    },
    "sub_label": {
        "ru": "Подписка: ",
        "en": "Subscription: ",
    },
    "thirty_days": {
        "ru": "30 дней",
        "en": "30 days",
    },
    "payment_expired": {
        "ru": "Время оплаты истекло. Создайте новый счёт. ",
        "en": "Payment expired. Create a new invoice. ",
    },
    "payment_pending": {
        "ru": "Оплата ещё не поступила. Попробуйте позже. ",
        "en": "Payment not received yet. Try again later. ",
    },
    "check_error": {
        "ru": "Ошибка проверки. Попробуйте позже. ",
        "en": "Check failed. Try again later. ",
    },
    "reminder_title": {
        "ru": "Напоминание",
        "en": "Reminder",
    },
    "sub_expires_in": {
        "ru": "Подписка истекает через ",
        "en": "Subscription expires in ",
    },
    "renew_to_keep": {
        "ru": "Продлите, чтобы сохранить доступ. ",
        "en": "Renew to keep access. ",
    },
    "sub_expired_title": {
        "ru": "Подписка истекла",
        "en": "Subscription expired",
    },
    "kicked_from_channel": {
        "ru": "Вы удалены из канала. ",
        "en": "You have been removed from the channel. ",
    },
    "subscribe_again": {
        "ru": "Оформите подписку заново для доступа. ",
        "en": "Subscribe again to regain access. ",
    },
    "hour_reminder_text": {
        "ru": "{hours} час",
        "en": "{hours} hour",
    },
    "day_1": {
        "ru": "день",
        "en": "day",
    },
    "day_2_4": {
        "ru": "дня",
        "en": "days",
    },
    "day_many": {
        "ru": "дней",
        "en": "days",
    },
}


def t(key: str, lang: str = "ru", **kwargs: Any) -> str:
    entry = TEXTS.get(key)
    if entry is None:
        return key

    text = entry.get(lang, entry.get("ru", key))

    if kwargs:
        text = text.format(**kwargs)

    return text


def pluralize_days(n: int, lang: str = "ru") -> str:
    if lang == "en":
        return t("day_1", lang) if n == 1 else t("day_many", lang)

    if n % 10 == 1 and n % 100 != 11:
        return t("day_1", lang)
    if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return t("day_2_4", lang)
    return t("day_many", lang)

# CryptoBot - Telegram Subscription Bot

Telegram-бот для продажи подписок на приватный канал с оплатой через Crypto Pay (CryptoBot).

## Возможности

- Оплата подписки $10/месяц через Crypto Pay (USDT)
- Генерация одноразовой invite-ссылки после оплаты
- Автоматические напоминания за 2-3 дня до окончания подписки
- Автоматический кик из канала при истечении подписки
- SQLite база данных для хранения пользователей и подписок

## Требования

- Python 3.12+
- Telegram Bot Token ([@BotFather](https://t.me/BotFather))
- Crypto Pay API Token ([@CryptoBot](https://t.me/CryptoBot) -> Crypto Pay -> My Apps)
- Приватный Telegram-канал, где бот является администратором

## Установка

1. Клонировать репозиторий:
```bash
git clone <repo-url>
cd cryptobot
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env, указав свои токены и ID канала
```

5. Запустить бота:
```bash
python -m bot.main
```

## Настройка

### Переменные окружения (.env)

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен Telegram-бота от @BotFather |
| `CRYPTO_PAY_TOKEN` | API-токен Crypto Pay из @CryptoBot |
| `CHANNEL_ID` | ID приватного канала (числовой, например `-1001234567890`) |

### Подготовка бота

1. Создать бота через [@BotFather](https://t.me/BotFather)
2. Добавить бота в приватный канал как **администратора** с правами:
   - Приглашение пользователей (Invite users via link)
   - Бан пользователей (Ban users)
3. Получить ID канала (можно через [@userinfobot](https://t.me/userinfobot) или переслав сообщение из канала)
4. Получить API-токен в [@CryptoBot](https://t.me/CryptoBot) -> Crypto Pay -> My Apps -> Create App

## Структура проекта

```
cryptobot/
├── bot/
│   ├── main.py              # Точка входа, запуск бота + scheduler
│   ├── config.py             # Конфигурация из .env
│   ├── handlers/
│   │   ├── start.py          # Команда /start
│   │   └── payment.py        # Обработка оплаты
│   ├── services/
│   │   ├── crypto_pay.py     # Интеграция с Crypto Pay API
│   │   ├── subscription.py   # Логика подписок
│   │   └── scheduler.py      # Планировщик уведомлений и киков
│   ├── database/
│   │   ├── db.py             # Подключение к SQLite
│   │   └── models.py         # Операции с базой данных
│   └── keyboards/
│       └── inline.py         # Inline-клавиатуры
├── .env.example
├── requirements.txt
└── README.md
```

## Как работает

1. Пользователь запускает бота командой `/start`
2. Нажимает "Купить подписку ($10/мес)"
3. Бот создает инвойс через Crypto Pay API
4. Пользователь оплачивает и нажимает "Проверить оплату"
5. Бот проверяет статус инвойса и при успешной оплате:
   - Создает одноразовую invite-ссылку в приватный канал
   - Отправляет ссылку пользователю
   - Сохраняет подписку в базе данных
6. Планировщик каждый час проверяет подписки:
   - За 3 дня до окончания — первое напоминание
   - За 2 дня — второе напоминание
   - При истечении — кик из канала + уведомление

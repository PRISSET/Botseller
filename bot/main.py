import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BotConfig, load_config
from bot.database.db import close_db, init_db
from bot.handlers import payment, start
from bot.services.crypto_pay import CryptoPayService
from bot.services.scheduler import SchedulerService
from bot.services.subscription import SubscriptionService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    os.makedirs("data", exist_ok=True)

    await init_db()

    bot = Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    crypto_pay = CryptoPayService(
        token=config.crypto_pay_token, testnet=config.crypto_pay_testnet
    )
    subscription_service = SubscriptionService(bot=bot, config=config)
    scheduler_service = SchedulerService(
        bot=bot, config=config, subscription_service=subscription_service
    )

    dp.update.middleware
    dp["config"] = config
    dp["crypto_pay"] = crypto_pay
    dp["subscription_service"] = subscription_service

    dp.include_router(start.router)
    dp.include_router(payment.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduler_service.check_subscriptions,
        "interval",
        minutes=config.scheduler_interval_minutes,
        id="check_subscriptions",
    )
    scheduler.start()
    logger.info(
        "Scheduler started (interval: %d min)",
        config.scheduler_interval_minutes,
    )

    mode = "TESTNET" if config.crypto_pay_testnet else "PRODUCTION"
    logger.info("Crypto Pay mode: %s", mode)
    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown()
        await crypto_pay.close()
        await close_db()
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())

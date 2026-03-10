from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class BotConfig:
    token: str
    crypto_pay_token: str
    channel_id: int
    crypto_pay_testnet: bool = True
    subscription_price: float = 7.0
    subscription_days: int = 30
    reminder_days_before: tuple[int, ...] = (15, 7, 3, 2, 1)
    reminder_hours_before: tuple[int, ...] = (1,)
    scheduler_interval_minutes: int = 2


def load_config() -> BotConfig:
    token = getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set")

    crypto_pay_token = getenv("CRYPTO_PAY_TOKEN")
    if not crypto_pay_token:
        raise ValueError("CRYPTO_PAY_TOKEN is not set")

    channel_id = getenv("CHANNEL_ID")
    if not channel_id:
        raise ValueError("CHANNEL_ID is not set")

    testnet = getenv("CRYPTO_PAY_TESTNET", "true").lower() in ("true", "1", "yes")

    return BotConfig(
        token=token,
        crypto_pay_token=crypto_pay_token,
        channel_id=int(channel_id),
        crypto_pay_testnet=testnet,
    )

from datetime import UTC, datetime, timedelta

from bot.database.db import get_db


def _now() -> datetime:
    return datetime.now(UTC)


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


async def upsert_user(
    user_id: int, username: str | None, first_name: str | None
) -> None:
    db = await get_db()
    await db.execute(
        (user_id, username, first_name),
    )
    await db.commit()


async def create_subscription(
    user_id: int,
    invoice_id: int,
    days: int = 30,
    invite_link: str | None = None,
) -> int:
    db = await get_db()
    expires_at = _now() + timedelta(days=days)
    cursor = await db.execute(
        (user_id, invoice_id, expires_at.isoformat(), invite_link),
    )
    await db.commit()
    return cursor.lastrowid


async def get_active_subscription(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        (user_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    return dict(row)


async def get_expiring_subscriptions(days_before: int) -> list[dict]:
    db = await get_db()
    target = _now() + timedelta(days=days_before)
    now = _now()
    cursor = await db.execute(
        (target.isoformat(), now.isoformat()),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_expired_subscriptions() -> list[dict]:
    db = await get_db()
    now = _now()
    cursor = await db.execute(
        (now.isoformat(),),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def extend_subscription(subscription_id: int, days: int = 30) -> str:
    db = await get_db()
    cursor = await db.execute(
        "SELECT expires_at FROM subscriptions WHERE id = ?",
        (subscription_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        raise ValueError(f"Subscription {subscription_id} not found")
    current_expires = _parse_dt(row[0])

    base = max(current_expires, _now())
    new_expires = base + timedelta(days=days)

    await db.execute(
        "UPDATE subscriptions SET expires_at = ?, reminder_3d = 0, reminder_2d = 0 WHERE id = ?",
        (new_expires.isoformat(), subscription_id),
    )
    await db.commit()
    return new_expires.isoformat()


async def deactivate_subscription(subscription_id: int) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE subscriptions SET is_active = 0 WHERE id = ?",
        (subscription_id,),
    )
    await db.commit()


async def mark_reminder_sent(subscription_id: int, days_before: int) -> None:
    db = await get_db()
    col = f"reminder_{days_before}d"
    await db.execute(
        f"UPDATE subscriptions SET {col} = 1 WHERE id = ?",
        (subscription_id,),
    )
    await db.commit()

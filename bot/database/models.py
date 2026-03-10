import json
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
        """
        INSERT INTO users (user_id, username, first_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
        """,
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
        """
        INSERT INTO subscriptions (user_id, invoice_id, expires_at, invite_link)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, invoice_id, expires_at.isoformat(), invite_link),
    )
    await db.commit()
    return cursor.lastrowid


async def get_active_subscription(user_id: int) -> dict | None:
    db = await get_db()
    cursor = await db.execute(
        """
        SELECT * FROM subscriptions
        WHERE user_id = ? AND is_active = 1
        ORDER BY expires_at DESC
        LIMIT 1
        """,
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
        """
        SELECT s.*, u.username, u.first_name
        FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.is_active = 1
          AND s.expires_at <= ?
          AND s.expires_at > ?
        """,
        (target.isoformat(), now.isoformat()),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


async def get_expired_subscriptions() -> list[dict]:
    db = await get_db()
    now = _now()
    cursor = await db.execute(
        """
        SELECT s.*, u.username, u.first_name
        FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.is_active = 1
          AND s.expires_at <= ?
        """,
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
        "UPDATE subscriptions SET expires_at = ?, reminder_3d = 0, reminder_2d = 0, reminders_sent = '[]' WHERE id = ?",
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


async def mark_reminder_sent(subscription_id: int, reminder_key: str) -> None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT reminders_sent FROM subscriptions WHERE id = ?",
        (subscription_id,),
    )
    row = await cursor.fetchone()
    sent: list[str] = []
    if row and row[0]:
        try:
            sent = json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            sent = []

    if reminder_key not in sent:
        sent.append(reminder_key)

    await db.execute(
        "UPDATE subscriptions SET reminders_sent = ? WHERE id = ?",
        (json.dumps(sent), subscription_id),
    )
    await db.commit()


async def get_reminders_sent(subscription_id: int) -> list[str]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT reminders_sent FROM subscriptions WHERE id = ?",
        (subscription_id,),
    )
    row = await cursor.fetchone()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return []
    return []


async def get_all_known_user_ids() -> list[int]:
    db = await get_db()
    cursor = await db.execute("SELECT user_id FROM users")
    rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def get_user_language(user_id: int) -> str | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT language FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = await cursor.fetchone()
    if row is None:
        return None
    return row[0]


async def set_user_language(user_id: int, language: str) -> None:
    db = await get_db()
    await db.execute(
        """
        INSERT INTO users (user_id, language)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET language = excluded.language
        """,
        (user_id, language),
    )
    await db.commit()

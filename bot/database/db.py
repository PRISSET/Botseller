import aiosqlite

DB_PATH = "data/bot.db"

_connection: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    global _connection
    if _connection is None:
        _connection = await aiosqlite.connect(DB_PATH)
        _connection.row_factory = aiosqlite.Row
    return _connection


async def init_db() -> None:
    db = await get_db()

    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            first_name  TEXT,
            language    TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

    try:
        await db.execute("ALTER TABLE users ADD COLUMN language TEXT")
    except Exception:
        pass

    await db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            invoice_id      INTEGER NOT NULL,
            started_at      TEXT NOT NULL DEFAULT (datetime('now')),
            expires_at      TEXT NOT NULL,
            is_active       INTEGER NOT NULL DEFAULT 1,
            reminder_3d     INTEGER NOT NULL DEFAULT 0,
            reminder_2d     INTEGER NOT NULL DEFAULT 0,
            reminders_sent  TEXT NOT NULL DEFAULT '[]',
            invite_link     TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    try:
        await db.execute(
            "ALTER TABLE subscriptions ADD COLUMN reminders_sent TEXT NOT NULL DEFAULT '[]'"
        )
    except Exception:
        pass

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_sub_user
        ON subscriptions(user_id)
    """)

    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_sub_active
        ON subscriptions(is_active, expires_at)
    """)

    await db.commit()


async def close_db() -> None:
    global _connection
    if _connection is not None:
        await _connection.close()
        _connection = None

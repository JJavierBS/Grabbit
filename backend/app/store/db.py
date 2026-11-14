"""SQLite connection and table registry.

Each team owns a `store/<domain>.py` that calls `register_table(...)` at import time with
a `CREATE TABLE IF NOT EXISTS` statement; `init_db()` runs them all in the lifespan. No
migrations in the MVP: changing a table means deleting the database file (backend.md).
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.config import get_settings

_table_sql: list[str] = []


def register_table(sql: str) -> None:
    if sql not in _table_sql:
        _table_sql.append(sql)


def registered_tables() -> tuple[str, ...]:
    return tuple(_table_sql)


def database_file() -> Path:
    return get_settings().database_file


def init_db(path: Path | None = None) -> None:
    target = path or database_file()
    target.parent.mkdir(parents=True, exist_ok=True)
    with connect(target) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        for sql in _table_sql:
            conn.execute(sql)


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Short-lived connection: commits on success, rolls back on error, always closes."""
    conn = sqlite3.connect(path or database_file(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

"""SQLite connection and table registry. Each domain module registers its own tables."""

import sqlite3
from pathlib import Path

from app.config import get_settings

_tables: list[str] = []
_conn: sqlite3.Connection | None = None


def register_table(ddl: str) -> None:
    if ddl not in _tables:
        _tables.append(ddl)


def init_db(path: str | None = None) -> sqlite3.Connection:
    global _conn
    close()
    db_path = path or get_settings().database_path
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # One uvicorn worker (architecture.md), so one shared connection is enough.
    _conn = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
    _conn.row_factory = sqlite3.Row
    for ddl in _tables:
        _conn.execute(ddl)
    return _conn


def conn() -> sqlite3.Connection:
    if _conn is None:
        return init_db()
    return _conn


def close() -> None:
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None

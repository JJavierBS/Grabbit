"""Cala response cache: every call is stored by method, path and request body."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from app.store.db import register_table

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cala_cache (
    key TEXT PRIMARY KEY,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    request TEXT NOT NULL,
    response TEXT NOT NULL,
    fetched_at TEXT NOT NULL
)
"""
register_table(TABLE_SQL)


def cache_key(method: str, path: str, params: dict[str, Any] | None, body: Any) -> str:
    request = json.dumps({"params": params or {}, "body": body}, sort_keys=True, default=str)
    digest = hashlib.sha256(request.encode()).hexdigest()
    return f"{method.upper()} {path} {digest}"


class CalaCache:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.execute(TABLE_SQL)
        self._conn.commit()

    def get(self, key: str) -> Any | None:
        row = self._conn.execute("SELECT response FROM cala_cache WHERE key = ?", (key,)).fetchone()
        return None if row is None else json.loads(row[0])

    def put(self, key: str, method: str, path: str, request: Any, response: Any) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO cala_cache VALUES (?, ?, ?, ?, ?, ?)",
            (
                key,
                method.upper(),
                path,
                json.dumps(request, sort_keys=True, default=str),
                json.dumps(response),
                datetime.now(UTC).isoformat(),
            ),
        )
        self._conn.commit()

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0]

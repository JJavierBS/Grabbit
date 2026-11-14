"""Cala response cache: every call is stored by method, path and request body.

SQLite always holds a copy, so local dev and replay mode work offline. With a Valkey the
responses are also shared by every deployed instance, and Valkey is read first.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from typing import Any

from app.store.db import register_table
from app.store.valkey import Valkey

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

VALKEY_PREFIX = "cala:"


def cache_key(method: str, path: str, params: dict[str, Any] | None, body: Any) -> str:
    request = json.dumps({"params": params or {}, "body": body}, sort_keys=True, default=str)
    digest = hashlib.sha256(request.encode()).hexdigest()
    return f"{method.upper()} {path} {digest}"


class CalaCache:
    def __init__(self, conn: sqlite3.Connection, valkey: Valkey | None = None):
        self._conn = conn
        self._valkey = valkey
        self._conn.execute(TABLE_SQL)
        self._conn.commit()

    def get(self, key: str) -> Any | None:
        if self._valkey is not None:
            shared = self._valkey.get(VALKEY_PREFIX + key)
            if shared is not None:
                return json.loads(shared)
        row = self._conn.execute("SELECT response FROM cala_cache WHERE key = ?", (key,)).fetchone()
        if row is None:
            return None
        if self._valkey is not None:
            self._valkey.set(VALKEY_PREFIX + key, row[0])
        return json.loads(row[0])

    def put(self, key: str, method: str, path: str, request: Any, response: Any) -> None:
        payload = json.dumps(response)
        self._conn.execute(
            "INSERT OR REPLACE INTO cala_cache VALUES (?, ?, ?, ?, ?, ?)",
            (
                key,
                method.upper(),
                path,
                json.dumps(request, sort_keys=True, default=str),
                payload,
                datetime.now(UTC).isoformat(),
            ),
        )
        self._conn.commit()
        if self._valkey is not None:
            self._valkey.set(VALKEY_PREFIX + key, payload)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0]

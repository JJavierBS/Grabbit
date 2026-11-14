"""Last known state per watched entity, and the alerts the watcher produced."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from app.models import Alert
from app.store.db import register_table

TABLES_SQL = [
    """CREATE TABLE IF NOT EXISTS snapshots (
        entity_id TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        taken_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS alerts (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        payload TEXT NOT NULL
    )""",
]
for _sql in TABLES_SQL:
    register_table(_sql)


class WatchStore:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        for sql in TABLES_SQL:
            self._conn.execute(sql)
        self._conn.commit()

    def snapshot(self, entity_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT payload FROM snapshots WHERE entity_id = ?", (entity_id,)
        ).fetchone()
        return None if row is None else json.loads(row[0])

    def save_snapshot(self, entity_id: str, payload: dict[str, Any], taken_at: datetime) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?)",
            (entity_id, json.dumps(payload, default=str), taken_at.isoformat()),
        )
        self._conn.commit()

    def has_alert(self, alert_id: str) -> bool:
        row = self._conn.execute("SELECT 1 FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        return row is not None

    def add_alert(self, alert: Alert) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO alerts VALUES (?, ?, ?)",
            (alert.id, alert.created_at.isoformat(), alert.model_dump_json()),
        )
        self._conn.commit()

    def alerts_since(self, since: datetime, *, simulated: bool | None = None) -> int:
        rows = self._conn.execute(
            "SELECT payload FROM alerts WHERE created_at >= ?", (since.isoformat(),)
        ).fetchall()
        alerts = [Alert.model_validate_json(r[0]) for r in rows]
        if simulated is not None:
            alerts = [a for a in alerts if a.simulated == simulated]
        return len(alerts)

    def alerts(self) -> list[Alert]:
        rows = self._conn.execute("SELECT payload FROM alerts ORDER BY created_at DESC").fetchall()
        return [Alert.model_validate_json(r[0]) for r in rows]

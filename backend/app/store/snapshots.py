"""Last known state per watched entity, and the alerts the watcher produced."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from app import workspace
from app.models import Alert
from app.store.db import drop_if_missing, register_table

# Per workspace: each visitor's watcher diffs against what that visitor was last shown.
TABLES_SQL = [
    """CREATE TABLE IF NOT EXISTS snapshots (
        workspace TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        payload TEXT NOT NULL,
        taken_at TEXT NOT NULL,
        PRIMARY KEY (workspace, entity_id)
    )""",
    """CREATE TABLE IF NOT EXISTS alerts (
        workspace TEXT NOT NULL,
        id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        payload TEXT NOT NULL,
        PRIMARY KEY (workspace, id)
    )""",
]
for _sql in TABLES_SQL:
    register_table(_sql)
drop_if_missing("snapshots", "workspace")
drop_if_missing("alerts", "workspace")


class WatchStore:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._workspace = workspace.current()
        for sql in TABLES_SQL:
            self._conn.execute(sql)
        self._conn.commit()

    def snapshot(self, entity_id: str) -> dict[str, Any] | None:
        row = self._conn.execute(
            "SELECT payload FROM snapshots WHERE workspace = ? AND entity_id = ?",
            (self._workspace, entity_id),
        ).fetchone()
        return None if row is None else json.loads(row[0])

    def save_snapshot(self, entity_id: str, payload: dict[str, Any], taken_at: datetime) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO snapshots (workspace, entity_id, payload, taken_at)"
            " VALUES (?, ?, ?, ?)",
            (self._workspace, entity_id, json.dumps(payload, default=str), taken_at.isoformat()),
        )
        self._conn.commit()

    def has_alert(self, alert_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM alerts WHERE workspace = ? AND id = ?", (self._workspace, alert_id)
        ).fetchone()
        return row is not None

    def add_alert(self, alert: Alert) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO alerts (workspace, id, created_at, payload) VALUES (?, ?, ?, ?)",
            (self._workspace, alert.id, alert.created_at.isoformat(), alert.model_dump_json()),
        )
        self._conn.commit()

    def alerts_since(self, since: datetime, *, simulated: bool | None = None) -> int:
        rows = self._conn.execute(
            "SELECT payload FROM alerts WHERE workspace = ? AND created_at >= ?",
            (self._workspace, since.isoformat()),
        ).fetchall()
        alerts = [Alert.model_validate_json(r[0]) for r in rows]
        if simulated is not None:
            alerts = [a for a in alerts if a.simulated == simulated]
        return len(alerts)

    def alerts(self) -> list[Alert]:
        rows = self._conn.execute(
            "SELECT payload FROM alerts WHERE workspace = ? ORDER BY created_at DESC",
            (self._workspace,),
        ).fetchall()
        return [Alert.model_validate_json(r[0]) for r in rows]

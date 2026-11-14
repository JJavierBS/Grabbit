"""Conversation messages."""

import uuid
from datetime import UTC, datetime

from app import workspace
from app.models import (
    ChatMessage,
    ChatRole,
    ExploredGraph,
    ProfileChange,
    ReplySource,
    WalkSummary,
)
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS chat_messages (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        workspace TEXT NOT NULL,
        id TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        message_json TEXT NOT NULL
    )"""
)
db.drop_if_missing("chat_messages", "workspace")


def add(
    role: ChatRole,
    text: str,
    *,
    profile_changes: list[ProfileChange] | None = None,
    report_id: str | None = None,
    ui: str | None = None,
    graph: ExploredGraph | None = None,
    walk: WalkSummary | None = None,
    sources: list[ReplySource] | None = None,
    now: datetime | None = None,
) -> ChatMessage:
    message = ChatMessage(
        id=f"msg-{uuid.uuid4().hex[:12]}",
        role=role,
        text=text,
        created_at=now or datetime.now(UTC),
        profile_changes=profile_changes or [],
        report_id=report_id,
        ui=ui,
        graph=graph,
        walk=walk,
        sources=sources or [],
    )
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (workspace, id, role, message_json) VALUES (?, ?, ?, ?)",
            (workspace.current(), message.id, role, message.model_dump_json()),
        )
    return message


def relink_report(old_ids: list[str], new_id: str) -> None:
    """Point messages whose report was superseded (never stored) at the report that was."""
    if not old_ids:
        return
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT id, message_json FROM chat_messages WHERE workspace = ?",
            (workspace.current(),),
        ).fetchall()
        for row in rows:
            message = ChatMessage.model_validate_json(row["message_json"])
            if message.report_id in old_ids:
                message.report_id = new_id
                conn.execute(
                    "UPDATE chat_messages SET message_json = ? WHERE id = ?",
                    (message.model_dump_json(), row["id"]),
                )


def all_messages() -> list[ChatMessage]:
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT message_json FROM chat_messages WHERE workspace = ? ORDER BY seq",
            (workspace.current(),),
        ).fetchall()
    return [ChatMessage.model_validate_json(r["message_json"]) for r in rows]


def last(n: int) -> list[ChatMessage]:
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT message_json FROM chat_messages WHERE workspace = ? ORDER BY seq DESC LIMIT ?",
            (workspace.current(), n),
        ).fetchall()
    return [ChatMessage.model_validate_json(r["message_json"]) for r in reversed(rows)]


def count_user_messages() -> int:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE workspace = ? AND role = 'user'",
            (workspace.current(),),
        ).fetchone()
    return row[0]

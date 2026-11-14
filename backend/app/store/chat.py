"""Conversation messages."""

import uuid
from datetime import UTC, datetime

from app.models import ChatMessage, ChatRole, ProfileChange
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS chat_messages (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        message_json TEXT NOT NULL
    )"""
)


def add(
    role: ChatRole,
    text: str,
    *,
    profile_changes: list[ProfileChange] | None = None,
    report_id: str | None = None,
    now: datetime | None = None,
) -> ChatMessage:
    message = ChatMessage(
        id=f"msg-{uuid.uuid4().hex[:12]}",
        role=role,
        text=text,
        created_at=now or datetime.now(UTC),
        profile_changes=profile_changes or [],
        report_id=report_id,
    )
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (id, role, message_json) VALUES (?, ?, ?)",
            (message.id, role, message.model_dump_json()),
        )
    return message


def all_messages() -> list[ChatMessage]:
    with db.connect() as conn:
        rows = conn.execute("SELECT message_json FROM chat_messages ORDER BY seq").fetchall()
    return [ChatMessage.model_validate_json(r["message_json"]) for r in rows]


def last(n: int) -> list[ChatMessage]:
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT message_json FROM chat_messages ORDER BY seq DESC LIMIT ?", (n,)
        ).fetchall()
    return [ChatMessage.model_validate_json(r["message_json"]) for r in reversed(rows)]


def count_user_messages() -> int:
    with db.connect() as conn:
        row = conn.execute("SELECT COUNT(*) FROM chat_messages WHERE role = 'user'").fetchone()
    return row[0]

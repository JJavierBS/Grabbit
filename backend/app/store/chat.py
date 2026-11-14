"""Conversation messages."""

import uuid
from datetime import UTC, datetime

from app.models import ChatMessage, ProfileChange
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS chat_messages (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT UNIQUE NOT NULL,
        message_json TEXT NOT NULL
    )"""
)


def add(
    role: str,
    text: str,
    *,
    profile_changes: list[ProfileChange] | None = None,
    report_id: str | None = None,
    now: datetime | None = None,
) -> ChatMessage:
    message = ChatMessage(
        id=uuid.uuid4().hex,
        role=role,
        text=text,
        created_at=now or datetime.now(UTC),
        profile_changes=profile_changes or [],
        report_id=report_id,
    )
    db.conn().execute(
        "INSERT INTO chat_messages (id, message_json) VALUES (?, ?)",
        (message.id, message.model_dump_json()),
    )
    return message


def all_messages() -> list[ChatMessage]:
    rows = db.conn().execute("SELECT message_json FROM chat_messages ORDER BY seq").fetchall()
    return [ChatMessage.model_validate_json(r["message_json"]) for r in rows]


def last(n: int) -> list[ChatMessage]:
    rows = (
        db.conn()
        .execute("SELECT message_json FROM chat_messages ORDER BY seq DESC LIMIT ?", (n,))
        .fetchall()
    )
    return [ChatMessage.model_validate_json(r["message_json"]) for r in reversed(rows)]


def count_user_messages() -> int:
    return sum(1 for m in all_messages() if m.role == "user")

"""Profile, its versions and the history of changes. Undo pops the latest version."""

import json
from datetime import UTC, datetime

from app.models import Profile, ProfileChange
from app.store import db

db.register_table(
    """CREATE TABLE IF NOT EXISTS profile_versions (
        version INTEGER PRIMARY KEY,
        profile_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )"""
)
db.register_table(
    """CREATE TABLE IF NOT EXISTS profile_changes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version INTEGER NOT NULL,
        field TEXT NOT NULL,
        before_json TEXT,
        after_json TEXT,
        reason TEXT NOT NULL,
        by TEXT NOT NULL
    )"""
)


def current(now: datetime | None = None) -> Profile:
    row = (
        db.conn()
        .execute("SELECT profile_json FROM profile_versions ORDER BY version DESC LIMIT 1")
        .fetchone()
    )
    if row:
        return Profile.model_validate_json(row["profile_json"])
    profile = Profile(version=1, updated_at=now or datetime.now(UTC))
    _insert(profile)
    return profile


def save_version(
    profile: Profile, changes: list[ProfileChange], now: datetime | None = None
) -> Profile:
    """Store `profile` as the next version with the changes that produced it."""
    version = current().version + 1
    saved = profile.model_copy(update={"version": version, "updated_at": now or datetime.now(UTC)})
    c = db.conn()
    c.execute("BEGIN")
    try:
        _insert(saved)
        c.executemany(
            "INSERT INTO profile_changes (version, field, before_json, after_json, reason, by)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (version, ch.field, json.dumps(ch.before), json.dumps(ch.after), ch.reason, ch.by)
                for ch in changes
            ],
        )
        c.execute("COMMIT")
    except Exception:
        c.execute("ROLLBACK")
        raise
    return saved


def history() -> list[ProfileChange]:
    rows = (
        db.conn()
        .execute(
            "SELECT version, field, before_json, after_json, reason, by FROM profile_changes"
            " ORDER BY version DESC, id DESC"
        )
        .fetchall()
    )
    return [
        ProfileChange(
            version=r["version"],
            field=r["field"],
            before=json.loads(r["before_json"]),
            after=json.loads(r["after_json"]),
            reason=r["reason"],
            by=r["by"],
        )
        for r in rows
    ]


def undo() -> Profile | None:
    """Drop the latest version and its changes. None when only the first version is left."""
    latest = current()
    if latest.version <= 1:
        return None
    c = db.conn()
    c.execute("BEGIN")
    c.execute("DELETE FROM profile_versions WHERE version = ?", (latest.version,))
    c.execute("DELETE FROM profile_changes WHERE version = ?", (latest.version,))
    c.execute("COMMIT")
    return current()


def _insert(profile: Profile) -> None:
    db.conn().execute(
        "INSERT INTO profile_versions (version, profile_json, created_at) VALUES (?, ?, ?)",
        (profile.version, profile.model_dump_json(), profile.updated_at.isoformat()),
    )

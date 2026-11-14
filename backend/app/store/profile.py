"""Profile, its versions and the history of changes. Undo pops the latest version."""

import json
from datetime import UTC, datetime

from app.models import Profile, ProfileChange, ProfileFilters, ProfileStyle
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
# Highest version ever issued. Undo deletes a version, but its number must never come back:
# chat messages keep pointing at it, and the frontend offers Undo by version.
db.register_table(
    """CREATE TABLE IF NOT EXISTS profile_version_seq (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        last INTEGER NOT NULL
    )"""
)


def default_profile(now: datetime | None = None) -> Profile:
    """Every field has a default, so the first report can run before onboarding ends."""
    return Profile(
        version=1,
        event_id=None,
        thesis="",
        filters=ProfileFilters(stages=[], sectors_in=[], sectors_out=[], countries=[]),
        reference_investors=[],
        style=ProfileStyle(length="medium", detail="plain", language="en", sections=[]),
        cadence="event",
        alert_threshold="medium",
        instructions="",
        updated_at=now or datetime.now(UTC),
    )


def current(now: datetime | None = None) -> Profile:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT profile_json FROM profile_versions ORDER BY version DESC LIMIT 1"
        ).fetchone()
        if row:
            return Profile.model_validate_json(row["profile_json"])
        profile = default_profile(now)
        _insert(conn, profile)
        return profile


def save_version(
    profile: Profile, changes: list[ProfileChange], now: datetime | None = None
) -> Profile:
    """Store `profile` as the next version with the changes that produced it."""
    latest = current(now).version
    with db.connect() as conn:
        row = conn.execute("SELECT last FROM profile_version_seq WHERE id = 1").fetchone()
        version = max(latest, row["last"] if row else 0) + 1
        conn.execute(
            "INSERT INTO profile_version_seq (id, last) VALUES (1, ?)"
            " ON CONFLICT(id) DO UPDATE SET last = excluded.last",
            (version,),
        )
        saved = profile.model_copy(
            update={"version": version, "updated_at": now or datetime.now(UTC)}
        )
        _insert(conn, saved)
        conn.executemany(
            "INSERT INTO profile_changes (version, field, before_json, after_json, reason, by)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [
                (version, ch.field, json.dumps(ch.before), json.dumps(ch.after), ch.reason, ch.by)
                for ch in changes
            ],
        )
    return saved


def history() -> list[ProfileChange]:
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT version, field, before_json, after_json, reason, by FROM profile_changes"
            " ORDER BY version DESC, id DESC"
        ).fetchall()
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
    with db.connect() as conn:
        conn.execute("DELETE FROM profile_versions WHERE version = ?", (latest.version,))
        conn.execute("DELETE FROM profile_changes WHERE version = ?", (latest.version,))
    return current()


def _insert(conn, profile: Profile) -> None:
    conn.execute(
        "INSERT INTO profile_versions (version, profile_json, created_at) VALUES (?, ?, ?)",
        (profile.version, profile.model_dump_json(), profile.updated_at.isoformat()),
    )

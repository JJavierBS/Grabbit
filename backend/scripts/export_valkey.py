"""Copy the shared Cala cache out of Valkey into a SQLite file: the demo snapshot.

Run from backend/: `VALKEY_URL=rediss://... uv run python -m scripts.export_valkey
<source.db> <snapshot.db> [--strip]`.

The source is copied with SQLite's backup API (safe with WAL) and never modified. Every
`cala:<key>` in Valkey becomes a `cala_cache` row; `CalaCache.get` looks rows up by key
only, so the request column, which Valkey does not keep, is stored as "{}". `--strip`
empties visitor state (chats, profiles, reports, alerts, snapshots) so the file can be
shared, keeping only the caches. Check the result before a demo with
`DATABASE_PATH=<snapshot.db> CALA_MODE=replay make warm ARGS=--check`.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from app.store.cala_cache import TABLE_SQL, VALKEY_PREFIX

# Tables a shared snapshot keeps; every other table is emptied by --strip.
KEEP = frozenset({"cala_cache", "context_dev_cache", "investor_names"})


class ScanClient(Protocol):
    def scan_iter(self, match: str, count: int) -> Iterable[str]: ...

    def get(self, name: str) -> str | None: ...


def copy_db(source: Path, out: Path) -> None:
    src = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    dst = sqlite3.connect(out)
    try:
        src.backup(dst)
    finally:
        src.close()
        dst.close()


def import_keys(conn: sqlite3.Connection, client: ScanClient) -> int:
    """Write every `cala:*` key into `cala_cache`; returns how many were written."""
    conn.execute(TABLE_SQL)
    now = datetime.now(UTC).isoformat()
    written = 0
    for name in client.scan_iter(match=VALKEY_PREFIX + "*", count=500):
        payload = client.get(name)
        key = name.removeprefix(VALKEY_PREFIX)
        parts = key.split(" ", 2)
        if payload is None or len(parts) != 3:
            continue
        method, path, _digest = parts
        conn.execute(
            "INSERT OR REPLACE INTO cala_cache VALUES (?, ?, ?, ?, ?, ?)",
            (key, method, path, "{}", payload, now),
        )
        written += 1
    conn.commit()
    return written


def strip(conn: sqlite3.Connection) -> list[str]:
    """Empty every table outside KEEP; returns the tables emptied."""
    tables = [
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        if row[0] not in KEEP
    ]
    for table in tables:
        conn.execute(f'DELETE FROM "{table}"')
    conn.commit()
    return tables


def export(source: Path, out: Path, client: ScanClient, *, strip_state: bool) -> dict[str, int]:
    if out.resolve() == source.resolve():
        raise ValueError("the snapshot must be a new file, not the source")
    copy_db(source, out)
    conn = sqlite3.connect(out)
    try:
        before = conn.execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0]
        written = import_keys(conn, client)
        if strip_state:
            strip(conn)
        after = conn.execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0]
        conn.execute("VACUUM")
    finally:
        conn.close()
    return {"valkey_keys": written, "rows_before": before, "rows_after": after}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--strip", action="store_true", help="drop visitor state")
    args = parser.parse_args()
    url = os.environ.get("VALKEY_URL")
    if not url:
        parser.error("set VALKEY_URL to the Valkey URI (rediss://...)")
    import redis

    client = redis.Redis.from_url(url, decode_responses=True, socket_timeout=30)
    counts = export(args.source, args.out, client, strip_state=args.strip)
    print(
        f"{counts['valkey_keys']} Valkey keys; cala_cache "
        f"{counts['rows_before']} -> {counts['rows_after']} rows; wrote {args.out}"
    )


if __name__ == "__main__":
    main()

"""Translations of third-party text, per source text and target language (#226).

Shared by every workspace: the text comes from Cala and the web, never from a visitor.
"""

import hashlib

from pydantic import BaseModel

from app.store import db

# Created on use too: this module is imported lazily, after init_db() ran in the lifespan,
# so a database from before #226 would otherwise never get the table (#236).
_TABLE = """CREATE TABLE IF NOT EXISTS translations (
        target TEXT NOT NULL,
        source_hash TEXT NOT NULL,
        language TEXT NOT NULL,
        language_name TEXT NOT NULL,
        text TEXT NOT NULL,
        PRIMARY KEY (target, source_hash)
    )"""
db.register_table(_TABLE)


class Translation(BaseModel):
    """`language` equal to the target means the source needs no translation."""

    language: str
    language_name: str = ""
    text: str


def get_many(texts: list[str], target: str) -> dict[str, Translation]:
    if not texts:
        return {}
    by_hash = {_hash(t): t for t in texts}
    marks = ",".join("?" * len(by_hash))
    with db.connect() as conn:
        conn.execute(_TABLE)
        rows = conn.execute(
            "SELECT source_hash, language, language_name, text FROM translations "
            f"WHERE target = ? AND source_hash IN ({marks})",
            (target, *by_hash),
        ).fetchall()
    return {
        by_hash[r["source_hash"]]: Translation(
            language=r["language"], language_name=r["language_name"], text=r["text"]
        )
        for r in rows
    }


def put_many(translations: dict[str, Translation], target: str) -> None:
    if not translations:
        return
    with db.connect() as conn:
        conn.execute(_TABLE)
        conn.executemany(
            "INSERT OR REPLACE INTO translations "
            "(target, source_hash, language, language_name, text) VALUES (?, ?, ?, ?, ?)",
            [
                (target, _hash(source), t.language, t.language_name, t.text)
                for source, t in translations.items()
            ],
        )


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

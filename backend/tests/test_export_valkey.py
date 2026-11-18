import json
import sqlite3
from pathlib import Path

import pytest

from app.store.cala_cache import TABLE_SQL, CalaCache, cache_key
from scripts.export_valkey import export


class FakeValkey:
    def __init__(self, data: dict[str, str]):
        self.data = data

    def scan_iter(self, match: str, count: int):
        prefix = match.removesuffix("*")
        return [k for k in self.data if k.startswith(prefix)]

    def get(self, name: str) -> str | None:
        return self.data.get(name)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "source.db"
    conn = sqlite3.connect(path)
    conn.execute(TABLE_SQL)
    conn.execute(
        "INSERT INTO cala_cache VALUES ('GET /v1/old abc', 'GET', '/v1/old', '{}', '1', 't')"
    )
    conn.execute("CREATE TABLE chat_messages (id TEXT, text TEXT)")
    conn.execute("INSERT INTO chat_messages VALUES ('m1', 'private')")
    conn.execute("CREATE TABLE investor_names (name TEXT, entity_id TEXT)")
    conn.execute("INSERT INTO investor_names VALUES ('Y Combinator', 'yc')")
    conn.commit()
    conn.close()
    return path


def test_copies_valkey_keys_into_a_new_file_that_cala_cache_can_read(source, tmp_path):
    key = cache_key("GET", "/v1/entities", {"name": "Y Combinator"}, None)
    valkey = FakeValkey(
        {f"cala:{key}": json.dumps({"id": "yc"}), "other:x": "ignored", "cala:bad": "1"}
    )
    out = tmp_path / "snapshot.db"

    counts = export(source, out, valkey, strip_state=False)

    assert counts == {"valkey_keys": 1, "rows_before": 1, "rows_after": 2}
    conn = sqlite3.connect(out)
    assert CalaCache(conn).get(key) == {"id": "yc"}
    assert conn.execute("SELECT method, path FROM cala_cache WHERE key = ?", (key,)).fetchone() == (
        "GET",
        "/v1/entities",
    )
    # The source is never touched.
    assert sqlite3.connect(source).execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0] == 1


def test_strip_empties_visitor_state_and_keeps_the_caches(source, tmp_path):
    out = tmp_path / "snapshot.db"

    export(source, out, FakeValkey({}), strip_state=True)

    conn = sqlite3.connect(out)
    assert conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM investor_names").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM cala_cache").fetchone()[0] == 1


def test_refuses_to_overwrite_the_source(source):
    with pytest.raises(ValueError):
        export(source, source, FakeValkey({}), strip_state=True)

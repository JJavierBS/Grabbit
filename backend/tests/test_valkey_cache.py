import json
import sqlite3

import pytest
import redis

from app.config import get_settings
from app.store.cala_cache import VALKEY_PREFIX, CalaCache
from app.store.valkey import COOLDOWN_S, Valkey, valkey_from_settings

KEY = "POST /v1/knowledge/query abc"
RESPONSE = {"results": [{"id": "e1"}]}


class FakeValkeyClient:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}
        self.failing = False
        self.calls = 0

    def get(self, name: str) -> str | None:
        self.calls += 1
        if self.failing:
            raise redis.ConnectionError("down")
        return self.data.get(name)

    def set(self, name: str, value: str) -> bool:
        self.calls += 1
        if self.failing:
            raise redis.TimeoutError("slow")
        self.data[name] = value
        return True


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def fake() -> FakeValkeyClient:
    return FakeValkeyClient()


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def shared_cache(conn: sqlite3.Connection, fake: FakeValkeyClient, clock: Clock) -> CalaCache:
    return CalaCache(conn, Valkey(fake, clock=clock))


def put(cache: CalaCache) -> None:
    cache.put(KEY, "post", "/v1/knowledge/query", {"body": {"input": "x"}}, RESPONSE)


def test_put_writes_valkey_and_sqlite(
    shared_cache: CalaCache, conn: sqlite3.Connection, fake: FakeValkeyClient
) -> None:
    put(shared_cache)
    assert json.loads(fake.data[VALKEY_PREFIX + KEY]) == RESPONSE
    assert CalaCache(conn).get(KEY) == RESPONSE


def test_get_reads_valkey_first(shared_cache: CalaCache, fake: FakeValkeyClient) -> None:
    fake.data[VALKEY_PREFIX + KEY] = json.dumps({"from": "valkey"})
    assert shared_cache.get(KEY) == {"from": "valkey"}


def test_sqlite_hit_is_copied_to_valkey(
    conn: sqlite3.Connection, shared_cache: CalaCache, fake: FakeValkeyClient
) -> None:
    put(CalaCache(conn))
    assert shared_cache.get(KEY) == RESPONSE
    assert json.loads(fake.data[VALKEY_PREFIX + KEY]) == RESPONSE


def test_miss_in_both_is_none(shared_cache: CalaCache) -> None:
    assert shared_cache.get(KEY) is None


def test_valkey_down_falls_back_to_sqlite(shared_cache: CalaCache, fake: FakeValkeyClient) -> None:
    put(shared_cache)
    fake.failing = True
    assert shared_cache.get(KEY) == RESPONSE
    put(shared_cache)
    assert shared_cache.count() == 1


def test_valkey_is_skipped_during_cooldown_then_retried(
    shared_cache: CalaCache, fake: FakeValkeyClient, clock: Clock
) -> None:
    fake.failing = True
    shared_cache.get(KEY)
    calls_after_failure = fake.calls
    shared_cache.get(KEY)
    put(shared_cache)
    assert fake.calls == calls_after_failure

    fake.failing = False
    clock.now += COOLDOWN_S + 1
    put(shared_cache)
    assert VALKEY_PREFIX + KEY in fake.data


def test_without_valkey_url_the_cache_is_sqlite_only() -> None:
    assert valkey_from_settings() is None


def test_valkey_url_builds_a_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VALKEY_URL", "rediss://user:pw@example.invalid:12345")
    get_settings.cache_clear()
    assert isinstance(valkey_from_settings(), Valkey)

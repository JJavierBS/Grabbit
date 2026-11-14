"""Optional shared cache in Aiven for Valkey. Every failure degrades to a miss, never an error."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from functools import lru_cache
from typing import Protocol

import redis

from app.config import get_settings

log = logging.getLogger(__name__)

TIMEOUT_S = 0.5
# After a failure, skip Valkey for a while so each Cala call does not pay the timeout again.
COOLDOWN_S = 30.0


class KeyValueClient(Protocol):
    def get(self, name: str) -> str | None: ...

    def set(self, name: str, value: str) -> object: ...


class Valkey:
    def __init__(
        self, client: KeyValueClient, *, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._client = client
        self._clock = clock
        self._down_until = 0.0

    def get(self, key: str) -> str | None:
        if self._is_down():
            return None
        try:
            return self._client.get(key)
        except redis.RedisError as err:
            self._mark_down(err)
            return None

    def set(self, key: str, value: str) -> None:
        if self._is_down():
            return
        try:
            self._client.set(key, value)
        except redis.RedisError as err:
            self._mark_down(err)

    def _is_down(self) -> bool:
        return self._clock() < self._down_until

    def _mark_down(self, err: redis.RedisError) -> None:
        log.warning("Valkey unavailable, using SQLite for %.0f s: %s", COOLDOWN_S, err)
        self._down_until = self._clock() + COOLDOWN_S


@lru_cache
def connect_valkey(url: str) -> Valkey:
    client = redis.Redis.from_url(
        url, socket_timeout=TIMEOUT_S, socket_connect_timeout=TIMEOUT_S, decode_responses=True
    )
    return Valkey(client)


def valkey_from_settings() -> Valkey | None:
    """The shared Valkey when `VALKEY_URL` is set, else None (SQLite only)."""
    url = get_settings().valkey_url
    return connect_valkey(url) if url else None

"""The only door to Cala: one queue, timeout, retry on 429, and a response cache.

Cala's rate limit is undocumented and has no Retry-After header (docs/agents/cala.md
"Rate limits and latency"), so calls are serial by default and back off exponentially.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import httpx

from app.store.cala_cache import CalaCache, cache_key

log = logging.getLogger(__name__)

BASE_URL = "https://api.cala.ai"
RETRY_STATUSES = {429, 500, 502, 503, 504}
Mode = Literal["live", "replay"]


class CalaError(Exception):
    """Cala answered with an error we cannot retry."""

    def __init__(self, status: int, message: str):
        super().__init__(f"Cala {status}: {message}")
        self.status = status


class CalaCacheMiss(Exception):
    """Replay mode asked for a call that was never cached; run `make warm` first."""


class CalaKeyMissing(CalaError, ValueError):
    """Live mode without `CALA_API_KEY`. A `CalaError`, so every caller's Cala fallback
    (fixture candidates, skipping a watcher run) also covers a fresh checkout."""

    def __init__(self) -> None:
        super().__init__(401, "CALA_API_KEY is required when CALA_MODE=live")


class CalaClient:
    def __init__(
        self,
        api_key: str | None,
        cache: CalaCache,
        *,
        mode: Mode = "live",
        base_url: str = BASE_URL,
        timeout: float = 60.0,
        max_concurrency: int = 1,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        http: httpx.AsyncClient | None = None,
    ):
        if mode == "live" and not api_key:
            raise CalaKeyMissing()
        self.mode = mode
        self._cache = cache
        self._sem = asyncio.Semaphore(max_concurrency)
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._sleep = sleep
        self._http = http or httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"X-API-KEY": api_key or ""},
        )
        self.calls_made = 0
        self.cache_hits = 0

    async def aclose(self) -> None:
        await self._http.aclose()

    async def search(
        self, name: str, entity_types: list[str] | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"name": name, "limit": limit}
        if entity_types:
            params["entity_types"] = entity_types
        data = await self._call("GET", "/v1/entities", params=params)
        return data.get("entities", [])

    async def lookup(self, scheme: str, value: str) -> dict[str, Any] | None:
        try:
            return await self._call("POST", "/v1/entities/lookup", body={scheme: value})
        except CalaError as err:
            if err.status == 404:
                return None
            raise

    async def introspect(self, entity_id: str) -> dict[str, Any]:
        return await self._call("GET", f"/v1/entities/{entity_id}/introspection")

    async def retrieve(
        self, entity_id: str, body: dict[str, Any] | None = None, *, fresh: bool = False
    ) -> dict[str, Any]:
        """`fresh=True` skips the cached copy (the watcher needs today's state) and
        stores the new one; in replay mode the cache is still the only source."""
        return await self._call("POST", f"/v1/entities/{entity_id}", body=body or {}, fresh=fresh)

    async def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: Any = None,
        fresh: bool = False,
    ) -> Any:
        key = cache_key(method, path, params, body)
        if not fresh or self.mode == "replay":
            cached = self._cache.get(key)
            if cached is not None:
                self.cache_hits += 1
                return cached
        if self.mode == "replay":
            raise CalaCacheMiss(f"{method} {path} is not in the cache")
        async with self._sem:
            data = await self._send(method, path, params, body)
        self._cache.put(key, method, path, {"params": params, "body": body}, data)
        return data

    async def _send(self, method: str, path: str, params: Any, body: Any) -> Any:
        attempt = 0
        while True:
            self.calls_made += 1
            try:
                resp = await self._http.request(method, path, params=params, json=body)
            except httpx.TransportError as exc:
                # Timeouts, refused connections, dropped reads: retried, then a CalaError,
                # so every caller's Cala fallback also covers a dead network.
                status = 504 if isinstance(exc, httpx.TimeoutException) else 503
                if attempt >= self._max_retries:
                    raise CalaError(status, f"{type(exc).__name__} on {method} {path}") from exc
            else:
                if resp.status_code < 400:
                    return resp.json()
                status = resp.status_code
                if status not in RETRY_STATUSES or attempt >= self._max_retries:
                    raise CalaError(status, resp.text[:300])
            delay = self._backoff_base * (2**attempt)
            log.warning("cala %s %s -> %s, retry in %.1fs", method, path, status, delay)
            await self._sleep(delay)
            attempt += 1

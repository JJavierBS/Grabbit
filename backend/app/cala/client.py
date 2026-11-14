"""The only door to Cala: one queue, timeout, retry on 429, and a response cache.

Cala's rate limit is undocumented and has no Retry-After header (docs/agents/cala.md
"Rate limits and latency"). Every client in the process shares one `CalaLimiter`: calls are
serial, spaced, and all of them pause after a 429, so a burst from the chat walk, a report
rebuild and the background jobs together stays under the limit instead of retrying 429s
(#119). Cached reads never wait.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import httpx

from app.store.cala_cache import CalaCache, cache_key

log = logging.getLogger(__name__)

BASE_URL = "https://api.cala.ai"
RETRY_STATUSES = {429, 500, 502, 503, 504}
Mode = Literal["live", "replay"]


class CalaLimiter:
    """At most `max_concurrency` Cala requests in flight, starts at least `min_interval`
    seconds apart, and a shared pause after a 429. One per process (`shared_limiter`).

    The semaphore is rebuilt per event loop: asyncio primitives bind to the loop that first
    uses them, and tests or scripts may run several loops in one process.
    """

    def __init__(
        self,
        max_concurrency: int = 1,
        min_interval: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ):
        self.max_concurrency = max(1, max_concurrency)
        self.min_interval = max(0.0, min_interval)
        self._clock = clock
        self._sleep = sleep
        self._loop: asyncio.AbstractEventLoop | None = None
        self._sem: asyncio.Semaphore | None = None
        self._gate: asyncio.Lock | None = None
        self._next_start = 0.0
        self.in_flight = 0
        self.peak = 0

    def _primitives(self) -> tuple[asyncio.Semaphore, asyncio.Lock]:
        loop = asyncio.get_running_loop()
        if self._loop is not loop or self._sem is None or self._gate is None:
            self._loop = loop
            self._sem = asyncio.Semaphore(self.max_concurrency)
            self._gate = asyncio.Lock()
        return self._sem, self._gate

    async def __aenter__(self) -> CalaLimiter:
        sem, gate = self._primitives()
        await sem.acquire()
        try:
            async with gate:  # one caller at a time claims the next start slot
                wait = self._next_start - self._clock()
                if wait > 0:
                    await self._sleep(wait)
                self._next_start = max(self._next_start, self._clock()) + self.min_interval
        except BaseException:
            sem.release()
            raise
        self.in_flight += 1
        self.peak = max(self.peak, self.in_flight)
        return self

    async def __aexit__(self, *exc: object) -> None:
        self.in_flight -= 1
        sem, _ = self._primitives()
        sem.release()

    def cool_down(self, seconds: float) -> None:
        """After a 429, nobody starts a new request for `seconds`."""
        self._next_start = max(self._next_start, self._clock() + seconds)


_shared: CalaLimiter | None = None


def shared_limiter() -> CalaLimiter:
    """The process-wide limiter, sized from `CALA_MAX_CONCURRENCY` and `CALA_MIN_INTERVAL_MS`."""
    global _shared
    if _shared is None:
        from app.config import get_settings

        settings = get_settings()
        _shared = CalaLimiter(settings.cala_max_concurrency, settings.cala_min_interval_ms / 1000)
    return _shared


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
        limiter: CalaLimiter | None = None,
        max_retries: int = 5,
        backoff_base: float = 1.0,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        http: httpx.AsyncClient | None = None,
    ):
        if mode == "live" and not api_key:
            raise CalaKeyMissing()
        self.mode = mode
        self._cache = cache
        self._limiter = limiter or shared_limiter()
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
        # Calls the cache could not answer: live requests, or CalaCacheMiss in replay.
        self.cache_misses = 0

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

    async def query(
        self,
        text: str,
        *,
        cache_only: bool = False,
        fresh: bool = False,
        http_timeout: float | None = None,
        max_retries: int | None = None,
    ) -> dict[str, Any]:
        """`POST /v1/knowledge/query`, used only for "latest news regarding <company>"
        (cala.md "News"). It takes about 45 s, so callers in the request path pass
        `cache_only=True` and a background job fills the cache. `http_timeout` overrides the
        client timeout for this call."""
        return await self._call(
            "POST",
            "/v1/knowledge/query",
            body={"input": text},
            fresh=fresh,
            cache_only=cache_only,
            http_timeout=http_timeout,
            max_retries=max_retries,
        )

    def has_cached_query(self, text: str) -> bool:
        key = cache_key("POST", "/v1/knowledge/query", None, {"input": text})
        return self._cache.get(key) is not None

    async def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: Any = None,
        fresh: bool = False,
        cache_only: bool = False,
        http_timeout: float | None = None,
        max_retries: int | None = None,
    ) -> Any:
        key = cache_key(method, path, params, body)
        if not fresh or self.mode == "replay":
            cached = self._cache.get(key)
            if cached is not None:
                self.cache_hits += 1
                return cached
        self.cache_misses += 1
        if self.mode == "replay" or cache_only:
            raise CalaCacheMiss(f"{method} {path} is not in the cache")
        data = await self._send(method, path, params, body, http_timeout, max_retries)
        self._cache.put(key, method, path, {"params": params, "body": body}, data)
        return data

    async def _send(
        self,
        method: str,
        path: str,
        params: Any,
        body: Any,
        http_timeout: float | None = None,
        max_retries: int | None = None,
    ) -> Any:
        retries = self._max_retries if max_retries is None else max_retries
        extra: dict[str, Any] = {} if http_timeout is None else {"timeout": http_timeout}
        attempt = 0
        while True:
            self.calls_made += 1
            try:
                async with self._limiter:
                    resp = await self._http.request(method, path, params=params, json=body, **extra)
            except httpx.TransportError as exc:
                # Timeouts, refused connections, dropped reads: retried, then a CalaError,
                # so every caller's Cala fallback also covers a dead network.
                status = 504 if isinstance(exc, httpx.TimeoutException) else 503
                if attempt >= retries:
                    raise CalaError(status, f"{type(exc).__name__} on {method} {path}") from exc
            else:
                if resp.status_code < 400:
                    return resp.json()
                status = resp.status_code
                if status not in RETRY_STATUSES or attempt >= retries:
                    raise CalaError(status, resp.text[:300])
            delay = self._backoff_base * (2**attempt)
            log.warning("cala %s %s -> %s, retry in %.1fs", method, path, status, delay)
            if status == 429:
                self._limiter.cool_down(delay)
            await self._sleep(delay)
            attempt += 1

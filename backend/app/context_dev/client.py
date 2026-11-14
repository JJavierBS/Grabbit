"""The only door to Context.dev. Soft signals only: callers label them web, unverified."""

import hashlib
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from app.store import db

log = logging.getLogger(__name__)

BASE_URL = "https://api.context.dev/v1"
CACHE_TTL = timedelta(hours=6)

db.register_table(
    """CREATE TABLE IF NOT EXISTS context_dev_cache (
        key TEXT PRIMARY KEY,
        response_json TEXT NOT NULL,
        fetched_at TEXT NOT NULL
    )"""
)


class ContextDevClient:
    """Failures never break a report: every call degrades to an empty result."""

    def __init__(
        self,
        *,
        api_key: str,
        offline: bool = False,
        timeout_s: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.api_key = api_key
        self.offline = offline
        self._timeout = timeout_s
        self._transport = transport

    @property
    def enabled(self) -> bool:
        return bool(self.api_key) or self.offline

    async def search_news(
        self,
        *,
        domain: str | None,
        name: str,
        source_domains: list[str],
        since: datetime,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Recent articles about one company, from the allow-list when it is set."""
        entity = {"type": "domain", "domain": domain} if domain else {"type": "name", "name": name}
        body: dict[str, Any] = {
            "searchBy": {"type": "entity", "entity": entity},
            "sortBy": {"type": "newest"},
            "limit": limit,
            "filterBy": {"date": {"from": int(since.timestamp() * 1000)}},
        }
        if source_domains:
            # The API takes at most 3 publisher domains per query.
            body["filterBy"]["sourceDomain"] = source_domains[:3]
        response = await self._post("/news/search", body)
        return list(response.get("data", [])) if response else []

    async def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any] | None:
        key = hashlib.sha256(f"POST {path} {json.dumps(body, sort_keys=True)}".encode()).hexdigest()
        cached = _cache_get(key, allow_stale=self.offline)
        if cached is not None or self.offline or not self.api_key:
            return cached
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(
            base_url=BASE_URL, timeout=self._timeout, transport=self._transport
        ) as client:
            for attempt in range(2):
                try:
                    response = await client.post(path, json=body, headers=headers)
                except httpx.HTTPError as exc:
                    log.warning("context.dev %s failed: %s", path, type(exc).__name__)
                    return None
                if response.status_code in (408, 429, 500, 502, 503, 504) and attempt == 0:
                    continue
                if response.status_code != 200:
                    log.warning(
                        "context.dev %s returned %s (request %s)",
                        path,
                        response.status_code,
                        response.headers.get("x-request-id"),
                    )
                    return None
                data = response.json()
                _cache_put(key, data)
                return data
        return None


def _cache_get(key: str, *, allow_stale: bool) -> dict[str, Any] | None:
    with db.connect() as conn:
        row = conn.execute(
            "SELECT response_json, fetched_at FROM context_dev_cache WHERE key = ?", (key,)
        ).fetchone()
    if row is None:
        return None
    fresh = datetime.now(UTC) - datetime.fromisoformat(row["fetched_at"]) < CACHE_TTL
    return json.loads(row["response_json"]) if fresh or allow_stale else None


def _cache_put(key: str, data: dict[str, Any]) -> None:
    with db.connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO context_dev_cache (key, response_json, fetched_at)"
            " VALUES (?, ?, ?)",
            (key, json.dumps(data), datetime.now(UTC).isoformat()),
        )

"""In-process events bus feeding /api/events (SSE)."""

import asyncio
from typing import Any

_subscribers: set[asyncio.Queue] = set()
_published: list[tuple[str, Any]] = []


def publish(kind: str, data: Any) -> None:
    _published.append((kind, data))
    del _published[:-100]
    for queue in list(_subscribers):
        queue.put_nowait((kind, data))


def subscribe() -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.add(queue)
    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    _subscribers.discard(queue)


def recent() -> list[tuple[str, Any]]:
    return list(_published)

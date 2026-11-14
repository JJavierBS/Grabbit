"""In-process event bus behind `GET /api/events`.

Producers call `publish("alert", alert)`; every open SSE connection gets its own
`Subscription`. One uvicorn worker only (architecture.md), so memory is enough.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Any, Literal, get_args

from pydantic import BaseModel

EventKind = Literal["alert", "report", "profile"]
EVENT_KINDS: tuple[str, ...] = get_args(EventKind)


@dataclass(frozen=True)
class Event:
    kind: EventKind
    data: str


def _to_json(payload: Any) -> str:
    if isinstance(payload, BaseModel):
        return payload.model_dump_json()
    return json.dumps(payload, default=str)


class Subscription:
    """Queue of events for one listener. Registered on creation; close it when done."""

    def __init__(self, bus: "EventBus", max_queue: int) -> None:
        self._bus = bus
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue)

    def _deliver(self, event: Event) -> None:
        # A stalled client must not grow memory without bound: drop its oldest event.
        if self._queue.full():
            self._queue.get_nowait()
        self._queue.put_nowait(event)

    async def get(self) -> Event:
        return await self._queue.get()

    def close(self) -> None:
        self._bus._subscribers.discard(self)

    def __aiter__(self) -> "Subscription":
        return self

    async def __anext__(self) -> Event:
        return await self.get()

    def __enter__(self) -> "Subscription":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


class EventBus:
    def __init__(self, max_queue: int = 100) -> None:
        self._max_queue = max_queue
        self._subscribers: set[Subscription] = set()

    def publish(self, kind: EventKind, payload: Any) -> int:
        """Send `payload` (a Pydantic model or JSON-able value) to every subscriber.

        Call it from code running on the event loop (handlers, scheduler jobs).
        Returns the number of subscribers reached.
        """
        if kind not in EVENT_KINDS:
            raise ValueError(f"unknown event kind: {kind}")
        event = Event(kind=kind, data=_to_json(payload))
        for subscription in list(self._subscribers):
            subscription._deliver(event)
        return len(self._subscribers)

    def subscribe(self) -> Subscription:
        subscription = Subscription(self, self._max_queue)
        self._subscribers.add(subscription)
        return subscription

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


bus = EventBus()
publish = bus.publish
subscribe = bus.subscribe

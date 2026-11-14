from collections.abc import AsyncIterator

from fastapi import APIRouter
from sse_starlette import EventSourceResponse, ServerSentEvent

from app.events import Subscription, subscribe

router = APIRouter(tags=["events"])

PING_SECONDS = 15


async def event_stream(
    subscription: Subscription,
) -> AsyncIterator[dict[str, str] | ServerSentEvent]:
    with subscription:
        # A comment frame first: proxies such as Vite's dev proxy hold the response headers
        # until the first body bytes, so without it the browser waits for the first ping.
        yield ServerSentEvent(comment="connected")
        async for event in subscription:
            yield {"event": event.kind, "data": event.data}


@router.get(
    "/events",
    response_class=EventSourceResponse,
    responses={200: {"content": {"text/event-stream": {}}}},
)
async def stream_events() -> EventSourceResponse:
    """Server-Sent Events: `alert` (Alert), `report` ({id}), `profile` (Profile)."""
    return EventSourceResponse(event_stream(subscribe()), ping=PING_SECONDS)

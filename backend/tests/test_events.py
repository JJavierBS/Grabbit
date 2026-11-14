import asyncio
import json

import pytest

from app.api.events import event_stream
from app.events import EventBus
from app.models import ReportRef


async def test_subscribers_receive_published_events_as_json():
    bus = EventBus()
    with bus.subscribe() as first, bus.subscribe() as second:
        reached = bus.publish("report", ReportRef(id="rep-1"))

        assert reached == 2
        for subscription in (first, second):
            event = await asyncio.wait_for(subscription.get(), timeout=1)
            assert event.kind == "report"
            assert json.loads(event.data) == {"id": "rep-1"}


async def test_closed_subscription_stops_receiving():
    bus = EventBus()
    subscription = bus.subscribe()
    subscription.close()

    assert bus.publish("profile", {"version": 2}) == 0
    assert bus.subscriber_count == 0


async def test_slow_subscriber_keeps_only_the_newest_events():
    bus = EventBus(max_queue=2)
    with bus.subscribe() as subscription:
        for version in range(3):
            bus.publish("profile", {"version": version})

        received = [json.loads((await subscription.get()).data)["version"] for _ in range(2)]

    assert received == [1, 2]


def test_unknown_kind_is_rejected():
    with pytest.raises(ValueError):
        EventBus().publish("unknown", {})  # type: ignore[arg-type]


async def test_event_stream_yields_sse_frames_and_unsubscribes_on_close():
    bus = EventBus()
    stream = event_stream(bus.subscribe())
    bus.publish("alert", {"id": "alr-1"})

    frame = await asyncio.wait_for(anext(stream), timeout=1)
    await stream.aclose()

    assert frame == {"event": "alert", "data": '{"id": "alr-1"}'}
    assert bus.subscriber_count == 0

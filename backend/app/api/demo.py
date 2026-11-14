from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter

from app import fixtures
from app.api.errors import ApiError
from app.cala.client import CalaCacheMiss, CalaClient, CalaError
from app.config import get_settings
from app.events import publish
from app.models import Alert, ErrorResponse, SimulateEventRequest
from app.references import resolve_references
from app.store import profile as profile_store
from app.store import reports as report_store
from app.store.cala_cache import CalaCache
from app.store.db import connect
from app.store.snapshots import WatchStore
from app.watcher.run import Watcher

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post(
    "/simulate-event",
    responses={403: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def simulate_event(request: SimulateEventRequest) -> Alert:
    settings = get_settings()
    if not settings.demo_mode:
        raise ApiError(403, "demo_mode_disabled", "Set DEMO_MODE=1 to simulate events.")
    event = fixtures.demo_event(request.fixture)
    if event is None:
        available = ", ".join(fixtures.demo_event_names())
        raise ApiError(
            404, "fixture_not_found", f"No demo event '{request.fixture}'. Try: {available}."
        )
    if "patch" in event:
        return await _through_watcher(request.fixture, event)
    # Alert-shaped fixture: a canned alert for frontend work before the cache is warm.
    alert = Alert.model_validate(
        {
            **event,
            "id": f"alr-{uuid4().hex[:12]}",
            "created_at": datetime.now(UTC),
            "simulated": True,
        }
    )
    publish("alert", alert)
    return alert


async def _through_watcher(name: str, event: dict[str, Any]) -> Alert:
    """A staged Cala change, sent through the real diff, scoring and delivery path."""
    settings = get_settings()
    latest = report_store.latest()
    profile = resolve_references(profile_store.current(), latest.candidates if latest else [])
    with connect() as conn:
        client = CalaClient(settings.cala_api_key or None, CalaCache(conn), mode=settings.cala_mode)
        try:
            alerts = await Watcher(client, WatchStore(conn), publish=publish).simulate(
                name, profile
            )
        except CalaCacheMiss as err:
            raise ApiError(
                409, "cache_miss", f"{err}. Run `make warm` for {event['entity_id']} first."
            ) from err
        except CalaError as err:
            raise ApiError(502, "cala_error", str(err)) from err
        finally:
            await client.aclose()
    if not alerts:
        raise ApiError(
            409,
            "no_alert",
            "The staged change produced no alert: already sent, or below the alert threshold.",
        )
    return alerts[0]

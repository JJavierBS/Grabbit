from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter

from app import fixtures
from app.api.errors import ApiError
from app.config import get_settings
from app.events import publish
from app.models import Alert, ErrorResponse, SimulateEventRequest

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/simulate-event", responses={403: {"model": ErrorResponse}})
def simulate_event(request: SimulateEventRequest) -> Alert:
    if not get_settings().demo_mode:
        raise ApiError(403, "demo_mode_disabled", "Set DEMO_MODE=1 to simulate events.")
    event = fixtures.demo_event(request.fixture)
    if event is None:
        available = ", ".join(fixtures.demo_event_names())
        raise ApiError(
            404, "fixture_not_found", f"No demo event '{request.fixture}'. Try: {available}."
        )
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

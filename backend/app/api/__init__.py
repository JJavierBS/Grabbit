from fastapi import APIRouter

from app.api import alerts, chat, demo, events, health, profile, reports, transcribe
from app.api.errors import ERROR_RESPONSES, ApiError

api_router = APIRouter(prefix="/api", responses=ERROR_RESPONSES)
for module in (health, profile, chat, transcribe, reports, alerts, events, demo):
    api_router.include_router(module.router)


@api_router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
def unknown_endpoint(path: str) -> None:
    raise ApiError(404, "not_found", f"No endpoint /api/{path}.")

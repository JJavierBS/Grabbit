from fastapi import APIRouter

from app.config import get_settings
from app.models import Health

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> Health:
    settings = get_settings()
    return Health(
        status="ok",
        cala_mode=settings.cala_mode,
        llm_mode=settings.llm_mode,
        demo_mode=settings.demo_mode,
    )

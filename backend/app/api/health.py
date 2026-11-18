from fastapi import APIRouter

from app.config import get_settings
from app.llm import LLMError, get_llm, providers
from app.models import Health

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> Health:
    settings = get_settings()
    try:
        answering = providers(get_llm())
    except LLMError:  # e.g. LLM_MODE=gemini without a key: report it, stay healthy
        answering = []
    return Health(
        status="ok",
        cala_mode=settings.cala_mode,
        llm_mode=settings.llm_mode,
        llm_providers=answering,
        demo_mode=settings.demo_mode,
    )

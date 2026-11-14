from functools import lru_cache

from app.config import get_settings
from app.context_dev.client import ContextDevClient

__all__ = ["ContextDevClient", "get_context_dev"]


@lru_cache
def get_context_dev() -> ContextDevClient:
    settings = get_settings()
    return ContextDevClient(
        api_key=settings.context_dev_api_key,
        # Replay is the offline demo mode: web signals then come only from the cache too.
        offline=settings.cala_mode == "replay",
    )

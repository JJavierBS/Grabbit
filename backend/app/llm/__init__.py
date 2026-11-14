from functools import lru_cache

from app.config import get_settings
from app.llm.types import (
    LLM,
    ChatResult,
    LLMError,
    Message,
    OnText,
    ToolCall,
    ToolResult,
    ToolSpec,
)

__all__ = [
    "LLM",
    "ChatResult",
    "LLMError",
    "Message",
    "OnText",
    "ToolCall",
    "ToolResult",
    "ToolSpec",
    "get_llm",
]


@lru_cache
def get_llm() -> LLM:
    settings = get_settings()
    if settings.llm_mode == "fake":
        from app.llm.fake import FakeLLM

        return FakeLLM()
    from app.llm.client import GeminiLLM

    return GeminiLLM(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        timeout_s=settings.gemini_timeout_s,
        thoughts=settings.gemini_thoughts,
    )

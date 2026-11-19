from functools import lru_cache

from app.config import get_settings
from app.llm.types import (
    LLM,
    ChatResult,
    LiveToken,
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
    "LiveToken",
    "LLMError",
    "Message",
    "OnText",
    "ToolCall",
    "ToolResult",
    "ToolSpec",
    "get_llm",
    "providers",
]


@lru_cache
def get_llm() -> LLM:
    settings = get_settings()
    mode = settings.llm_mode
    if mode == "fake":
        from app.llm.fake import FakeLLM

        return FakeLLM()
    if mode == "scripted":
        return _scripted()
    if mode == "gemini":
        return _gemini()
    if mode == "openai":
        return _openai_compat()
    return _auto()


def providers(llm: LLM) -> list[str]:
    """Who can answer now, in order, for /api/health: a provider sitting out is left out."""
    from app.llm.chain import ChainLLM
    from app.llm.fake import FakeLLM

    if isinstance(llm, ChainLLM):
        return llm.available
    if isinstance(llm, FakeLLM):
        return ["scripted"]
    return [get_settings().llm_mode]


def _auto() -> LLM:
    """Every model a key is set for, then the scripted demo, which never fails."""
    from app.llm.chain import ChainLLM

    settings = get_settings()
    chain: list[tuple[str, LLM]] = []
    if settings.gemini_api_key:
        chain.append(("gemini", _gemini()))
    if settings.openai_compat_api_key:
        chain.append(("openai", _openai_compat()))
    chain.append(("scripted", _scripted()))
    return ChainLLM(chain)


def _scripted() -> LLM:
    from app.llm.fake import DEMO_SCRIPTS_DIR, SCRIPTS_DIR, FakeLLM, load_scripts

    # The demo path first; the test scripts answer anything it does not cover.
    return FakeLLM(load_scripts(DEMO_SCRIPTS_DIR) + load_scripts(SCRIPTS_DIR))


def _gemini() -> LLM:
    from app.llm.client import GeminiLLM

    settings = get_settings()
    return GeminiLLM(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
        timeout_s=settings.gemini_timeout_s,
        thoughts=settings.gemini_thoughts,
        live_transcribe_model=settings.gemini_live_transcribe_model,
        lite_model=settings.gemini_lite_model,
    )


def _openai_compat() -> LLM:
    from app.llm.openai_compat import OpenAICompatLLM

    settings = get_settings()
    return OpenAICompatLLM(
        api_key=settings.openai_compat_api_key,
        base_url=settings.openai_compat_base_url,
        model=settings.openai_compat_model,
        lite_model=settings.openai_compat_lite_model,
        transcribe_model=settings.openai_compat_transcribe_model,
        timeout_s=settings.gemini_timeout_s,
    )

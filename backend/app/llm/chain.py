"""Several models behind one door: each call goes to the first one that answers.

`LLM_MODE=auto` puts Gemini first, then an OpenAI-compatible API, then the scripted demo,
which never fails. A provider that fails sits out for a while (like Valkey in
store/valkey.py), so a rate-limited free tier is not retried on every call.
"""

import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from app.llm.types import LLM, ChatResult, LiveToken, LLMError, Message, OnText, T, ToolSpec

log = logging.getLogger(__name__)

COOLDOWN_S = 60.0


class ChainLLM:
    def __init__(
        self,
        providers: list[tuple[str, LLM]],
        *,
        clock: Callable[[], float] = time.monotonic,
        cooldown_s: float = COOLDOWN_S,
    ) -> None:
        if not providers:
            raise LLMError("the LLM chain needs at least one provider")
        self.providers = providers
        self._clock = clock
        self._cooldown_s = cooldown_s
        self._down_until: dict[str, float] = {}

    @property
    def names(self) -> list[str]:
        return [name for name, _ in self.providers]

    async def chat(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
        on_text: OnText | None = None,
    ) -> ChatResult:
        return await self._first(
            "chat",
            lambda llm: llm.chat(system=system, messages=messages, tools=tools, on_text=on_text),
        )

    async def generate(
        self,
        *,
        task: str,
        system: str,
        prompt: str,
        schema: type[T],
        quick: bool = False,
        lite: bool = False,
    ) -> T:
        return await self._first(
            task,
            lambda llm: llm.generate(
                task=task, system=system, prompt=prompt, schema=schema, quick=quick, lite=lite
            ),
        )

    async def transcribe(self, *, audio: bytes, mime_type: str) -> str:
        return await self._first(
            "transcribe", lambda llm: llm.transcribe(audio=audio, mime_type=mime_type)
        )

    async def live_token(self) -> LiveToken:
        return await self._first("live_token", lambda llm: llm.live_token(), cool=False)

    async def _first(
        self, task: str, call: Callable[[LLM], Awaitable[Any]], *, cool: bool = True
    ) -> Any:
        """The first provider's answer. `cool=False`: a missing feature, not an outage."""
        now = self._clock()
        ready = [(n, p) for n, p in self.providers if self._down_until.get(n, 0.0) <= now]
        # Everyone resting: try them all anyway rather than fail the visitor.
        last: LLMError | None = None
        for name, provider in ready or self.providers:
            try:
                answer = await call(provider)
            except LLMError as exc:
                last = exc
                # The last provider is the floor (the scripted demo): it never sits out.
                if cool and name != self.providers[-1][0]:
                    self._down_until[name] = self._clock() + self._cooldown_s
                log.info("llm chain: %s failed %s (%s), trying the next", name, task, exc)
                continue
            log.info("llm chain: %s answered %s", name, task)
            return answer
        raise last or LLMError(f"{task}: no provider answered")

"""The only door to Gemini (google-genai SDK)."""

import logging
import time

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.llm.types import ChatResult, LLMError, Message, T, ToolCall, ToolSpec

log = logging.getLogger(__name__)


class GeminiLLM:
    def __init__(self, *, api_key: str, model: str, timeout_s: float = 30.0) -> None:
        if not api_key or not model:
            raise LLMError("GEMINI_API_KEY and GEMINI_MODEL are required with LLM_MODE=gemini")
        self.model = model
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=int(timeout_s * 1000),
                retry_options=types.HttpRetryOptions(
                    attempts=3, initial_delay=1.0, http_status_codes=[429, 500, 502, 503, 504]
                ),
            ),
        )

    async def chat(
        self, *, system: str, messages: list[Message], tools: list[ToolSpec] | None = None
    ) -> ChatResult:
        config = types.GenerateContentConfig(system_instruction=system, temperature=0.3)
        if tools:
            config.tools = [
                types.Tool(
                    function_declarations=[
                        types.FunctionDeclaration(
                            name=t.name,
                            description=t.description,
                            parameters_json_schema=t.parameters,
                        )
                        for t in tools
                    ]
                )
            ]
            config.automatic_function_calling = types.AutomaticFunctionCallingConfig(disable=True)
        response = await self._call("chat", _contents(messages), config)
        calls = [
            ToolCall(name=c.name or "", args=dict(c.args or {}))
            for c in response.function_calls or []
        ]
        return ChatResult(text=_text(response), tool_calls=calls)

    async def generate(self, *, task: str, system: str, prompt: str, schema: type[T]) -> T:
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.2,
            response_mime_type="application/json",
            response_json_schema=schema.model_json_schema(),
        )
        response = await self._call(task, _contents([Message(role="user", text=prompt)]), config)
        try:
            return schema.model_validate_json(_text(response))
        except ValidationError as exc:
            raise LLMError(f"{task}: structured output did not validate") from exc

    async def _call(self, task: str, contents, config):
        started = time.monotonic()
        try:
            response = await self._client.aio.models.generate_content(
                model=self.model, contents=contents, config=config
            )
        except errors.APIError as exc:
            log.warning("gemini %s failed: %s %s", task, exc.code, exc.status)
            raise LLMError(f"{task}: Gemini returned {exc.code}") from exc
        except Exception as exc:
            log.warning("gemini %s failed: %s", task, type(exc).__name__)
            raise LLMError(f"{task}: Gemini unreachable") from exc
        log.info("gemini %s took %.2fs", task, time.monotonic() - started)
        return response


def _contents(messages: list[Message]) -> list[types.Content]:
    return [types.Content(role=m.role, parts=[types.Part(text=m.text)]) for m in messages]


def _text(response) -> str:
    # response.text warns and returns None when the reply holds only function calls.
    parts = response.candidates[0].content.parts if response.candidates else None
    return "".join(p.text for p in parts or [] if p.text and not p.thought).strip()

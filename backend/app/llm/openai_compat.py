"""Any OpenAI-compatible chat API (Groq by default), the free fallback after Gemini.

Speaks plain HTTP through httpx: `/chat/completions` for chat with tools and for JSON
answers, `/audio/transcriptions` (Whisper) for Talk's recorded fallback. There is no Live
API here, so `live_token` fails and the browser records instead (useDictation.ts).
"""

import asyncio
import json
import logging
import time
from typing import Any

import httpx
from pydantic import ValidationError

from app.llm.types import ChatResult, LiveToken, LLMError, Message, OnText, T, ToolCall, ToolSpec

log = logging.getLogger(__name__)

# 429 moves the chain on at once; a 5xx is worth one more try.
RETRY_STATUS = {500, 502, 503, 504}


class OpenAICompatLLM:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        lite_model: str = "",
        transcribe_model: str = "",
        timeout_s: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key or not base_url or not model:
            raise LLMError("OPENAI_COMPAT_API_KEY, _BASE_URL and _MODEL are required")
        self.model = model
        self.lite_model = lite_model or model
        self.transcribe_model = transcribe_model
        self._client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/") + "/",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout_s,
        )

    async def chat(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
        on_text: OnText | None = None,
    ) -> ChatResult:
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, *_messages(messages)],
            "temperature": 0.3,
        }
        if tools:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters,
                    },
                }
                for t in tools
            ]
        message = (await self._post("chat", "chat/completions", json=body))["message"]
        text = (message.get("content") or "").strip()
        calls = [_tool_call(c) for c in message.get("tool_calls") or []]
        if on_text and text:
            on_text(text)
        return ChatResult(text=text, tool_calls=calls)

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
        instructions = (
            f"{system}\n\nAnswer with one JSON object, and nothing else, that validates "
            f"against this JSON schema:\n{json.dumps(schema.model_json_schema())}"
        )
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ]
        for attempt in range(2):
            body = {
                "model": self.lite_model if (lite or quick) else self.model,
                "messages": messages,
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }
            content = (await self._post(task, "chat/completions", json=body))["message"].get(
                "content"
            ) or ""
            try:
                return schema.model_validate_json(content)
            except ValidationError as exc:
                if attempt:
                    raise LLMError(f"{task}: structured output did not validate") from exc
                messages = [
                    *messages,
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": f"That JSON did not validate: {exc}. Fix it."},
                ]
        raise AssertionError("unreachable")

    async def transcribe(self, *, audio: bytes, mime_type: str) -> str:
        if not self.transcribe_model:
            raise LLMError("transcribe: OPENAI_COMPAT_TRANSCRIBE_MODEL is not set")
        ext = mime_type.split("/")[-1].split(";")[0] or "webm"
        data = await self._post(
            "transcribe",
            "audio/transcriptions",
            files={"file": (f"audio.{ext}", audio, mime_type)},
            data={"model": self.transcribe_model},
        )
        return (data.get("text") or "").strip()

    async def live_token(self) -> LiveToken:
        raise LLMError("live transcription needs Gemini")

    async def _post(self, task: str, path: str, **kwargs: Any) -> dict[str, Any]:
        """The first choice of a chat completion, or the whole body of any other call."""
        started = time.monotonic()
        for attempt in range(2):
            try:
                response = await self._client.post(path, **kwargs)
            except httpx.HTTPError as exc:
                log.warning("openai-compat %s failed: %s", task, type(exc).__name__)
                raise LLMError(f"{task}: provider unreachable") from exc
            if response.status_code in RETRY_STATUS and not attempt:
                await asyncio.sleep(1.0)
                continue
            break
        if response.status_code >= 400:
            log.warning("openai-compat %s failed: %s", task, response.status_code)
            raise LLMError(
                f"{task}: provider returned {response.status_code}",
                auth=response.status_code in (401, 403),
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise LLMError(f"{task}: provider returned no JSON") from exc
        log.info("openai-compat %s took %.2fs", task, time.monotonic() - started)
        if path != "chat/completions":
            return data
        choices = data.get("choices") or []
        if not choices:
            raise LLMError(f"{task}: provider returned no choices")
        return choices[0]


def _tool_call(raw: dict[str, Any]) -> ToolCall:
    function = raw.get("function") or {}
    try:
        args = json.loads(function.get("arguments") or "{}")
    except json.JSONDecodeError as exc:
        raise LLMError("chat: tool call arguments are not JSON") from exc
    return ToolCall(name=function.get("name") or "", args=args, id=raw.get("id"))


def _messages(messages: list[Message]) -> list[dict[str, Any]]:
    """Our turns as OpenAI messages: tool calls on the assistant, results as `tool` turns."""
    out: list[dict[str, Any]] = []
    last_ids: dict[str, str] = {}
    for n, m in enumerate(messages):
        if m.role == "model":
            turn: dict[str, Any] = {"role": "assistant", "content": m.text or None}
            if m.tool_calls:
                last_ids = {}
                calls = []
                for i, c in enumerate(m.tool_calls):
                    call_id = c.id or f"call_{n}_{i}"
                    last_ids.setdefault(c.name, call_id)
                    calls.append(
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {"name": c.name, "arguments": json.dumps(c.args)},
                        }
                    )
                turn["tool_calls"] = calls
            out.append(turn)
            continue
        for r in m.tool_results:
            call_id = r.id or last_ids.get(r.name, f"call_{r.name}")
            out.append({"role": "tool", "tool_call_id": call_id, "content": r.output})
        if m.text or not m.tool_results:
            out.append({"role": "user", "content": m.text})
    return out

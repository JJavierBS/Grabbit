"""The only door to Gemini (google-genai SDK)."""

import logging
import time
from datetime import UTC, datetime, timedelta

from google import genai
from google.genai import errors, types
from pydantic import ValidationError

from app.llm.types import ChatResult, LiveToken, LLMError, Message, OnText, T, ToolCall, ToolSpec

log = logging.getLogger(__name__)

# The Live API closes a transcription session after 10 minutes anyway.
LIVE_SESSION_MINUTES = 10

TRANSCRIBE_SYSTEM = (
    "Transcribe the speech in this recording word for word, in the language it is spoken in. "
    "Return only the transcript: no notes, labels or quotes. If nobody speaks, return nothing."
)


class GeminiLLM:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_s: float = 30.0,
        thoughts: bool = False,
        live_transcribe_model: str = "",
        lite_model: str = "",
    ) -> None:
        if not api_key or not model:
            raise LLMError("GEMINI_API_KEY and GEMINI_MODEL are required with LLM_MODE=gemini")
        self.model = model
        self.thoughts = thoughts
        self.live_transcribe_model = live_transcribe_model
        self.lite_model = lite_model or model
        # Ephemeral tokens and the Live API exist only on v1beta.
        self._live_client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(api_version="v1beta", timeout=int(timeout_s * 1000)),
        )
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
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
        on_text: OnText | None = None,
    ) -> ChatResult:
        config = types.GenerateContentConfig(system_instruction=system, temperature=0.3)
        if self.thoughts:
            config.thinking_config = types.ThinkingConfig(include_thoughts=True)
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
        if on_text:
            parts = await self._stream("chat", _contents(messages), config, on_text)
        else:
            response = await self._call("chat", _contents(messages), config)
            parts = response.candidates[0].content.parts if response.candidates else None
        calls = [
            ToolCall(
                name=p.function_call.name or "",
                args=dict(p.function_call.args or {}),
                id=p.function_call.id,
                signature=p.thought_signature,
            )
            for p in parts or []
            if p.function_call
        ]
        return ChatResult(text=_text(parts), tool_calls=calls, thoughts=_thoughts(parts))

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
        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.2,
            response_mime_type="application/json",
            response_json_schema=schema.model_json_schema(),
        )
        if quick or lite:
            # Picking and wording a few lines needs no deep reasoning: ~2 s instead of ~13 s.
            config.thinking_config = types.ThinkingConfig(thinking_level="minimal")
        model = self.lite_model if lite else self.model
        contents = _contents([Message(role="user", text=prompt)])
        response = await self._call(task, contents, config, model=model)
        try:
            return schema.model_validate_json(_text(_parts_of(response)))
        except ValidationError as exc:
            raise LLMError(f"{task}: structured output did not validate") from exc

    async def transcribe(self, *, audio: bytes, mime_type: str) -> str:
        config = types.GenerateContentConfig(system_instruction=TRANSCRIBE_SYSTEM, temperature=0.0)
        contents = [
            types.Content(
                role="user", parts=[types.Part.from_bytes(data=audio, mime_type=mime_type)]
            )
        ]
        return _text(_parts_of(await self._call("transcribe", contents, config)))

    async def live_token(self) -> LiveToken:
        """One Live API transcription session for the browser, locked to Talk's config."""
        if not self.live_transcribe_model:
            raise LLMError("GEMINI_LIVE_TRANSCRIBE_MODEL is not set")
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=LIVE_SESSION_MINUTES)
        try:
            token = await self._live_client.aio.auth_tokens.create(
                config=types.CreateAuthTokenConfig(
                    uses=1,
                    expire_time=expires_at,
                    new_session_expire_time=now + timedelta(minutes=1),
                    live_connect_constraints=types.LiveConnectConstraints(
                        model=self.live_transcribe_model,
                        config=types.LiveConnectConfig(
                            response_modalities=[types.Modality.TEXT],
                            # Auto language; SMART drops "eh", fixes punctuation and numbers.
                            input_audio_transcription=types.AudioTranscriptionConfig(
                                language_codes=[], mode="SMART"
                            ),
                        ),
                    ),
                )
            )
        except errors.APIError as exc:
            log.warning("gemini live token failed: %s %s", exc.code, exc.status)
            raise LLMError(f"live_token: Gemini returned {exc.code}", auth=_refused(exc)) from exc
        except Exception as exc:
            log.warning("gemini live token failed: %s", type(exc).__name__)
            raise LLMError("live_token: Gemini unreachable") from exc
        if not token.name:
            raise LLMError("live_token: Gemini returned no token")
        return LiveToken(token=token.name, model=self.live_transcribe_model, expires_at=expires_at)

    async def _stream(self, task: str, contents, config, on_text: OnText) -> list[types.Part]:
        """Stream the reply, telling `on_text` the answer so far; returns every part seen."""
        started = time.monotonic()
        parts: list[types.Part] = []
        text = ""
        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=self.model, contents=contents, config=config
            )
            async for chunk in stream:
                for part in _parts_of(chunk):
                    parts.append(part)
                    if part.text and not part.thought:
                        text += part.text
                        on_text(text)
        except errors.APIError as exc:
            log.warning("gemini %s stream failed: %s %s", task, exc.code, exc.status)
            raise LLMError(f"{task}: Gemini returned {exc.code}", auth=_refused(exc)) from exc
        except Exception as exc:
            log.warning("gemini %s stream failed: %s", task, type(exc).__name__)
            raise LLMError(f"{task}: Gemini unreachable") from exc
        log.info("gemini %s streamed in %.2fs", task, time.monotonic() - started)
        return parts

    async def _call(self, task: str, contents, config, *, model: str | None = None):
        started = time.monotonic()
        try:
            response = await self._client.aio.models.generate_content(
                model=model or self.model, contents=contents, config=config
            )
        except errors.APIError as exc:
            log.warning("gemini %s failed: %s %s", task, exc.code, exc.status)
            raise LLMError(f"{task}: Gemini returned {exc.code}", auth=_refused(exc)) from exc
        except Exception as exc:
            log.warning("gemini %s failed: %s", task, type(exc).__name__)
            raise LLMError(f"{task}: Gemini unreachable") from exc
        log.info("gemini %s took %.2fs", task, time.monotonic() - started)
        return response


def _refused(exc: errors.APIError) -> bool:
    """The key was refused. Gemini answers a revoked key with 400 API_KEY_INVALID, not 401."""
    return exc.code in (401, 403) or "API_KEY_INVALID" in str(exc.details)


def _parts_of(response) -> list[types.Part]:
    return (response.candidates[0].content.parts if response.candidates else None) or []


def _contents(messages: list[Message]) -> list[types.Content]:
    return [types.Content(role=m.role, parts=_parts(m)) for m in messages]


def _parts(m: Message) -> list[types.Part]:
    parts = [
        types.Part(
            function_response=types.FunctionResponse(
                id=r.id, name=r.name, response={"result": r.output}
            )
        )
        for r in m.tool_results
    ]
    if m.text or not (m.tool_calls or m.tool_results):
        parts.append(types.Part(text=m.text))
    parts += [
        types.Part(
            function_call=types.FunctionCall(id=c.id, name=c.name, args=c.args),
            thought_signature=c.signature,
        )
        for c in m.tool_calls
    ]
    return parts


def _text(parts: list[types.Part] | None) -> str:
    # response.text warns and returns None when the reply holds only function calls.
    return "".join(p.text for p in parts or [] if p.text and not p.thought).strip()


def _thoughts(parts: list[types.Part] | None) -> str:
    return "".join(p.text for p in parts or [] if p.text and p.thought).strip()

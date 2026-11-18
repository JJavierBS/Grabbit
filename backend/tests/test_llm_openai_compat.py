import json

import httpx
import pytest
import respx
from pydantic import BaseModel

from app.llm import LLMError, Message, ToolCall, ToolResult, ToolSpec
from app.llm.openai_compat import OpenAICompatLLM

BASE = "https://llm.test/v1"


def make_llm() -> OpenAICompatLLM:
    return OpenAICompatLLM(
        api_key="k",
        base_url=BASE,
        model="big",
        lite_model="small",
        transcribe_model="whisper",
    )


def completion(message: dict) -> httpx.Response:
    return httpx.Response(200, json={"choices": [{"message": message}]})


class Verdict(BaseModel):
    rewrite: bool
    reason: str = ""


@respx.mock
async def test_tool_calls_round_trip_as_openai_tool_messages():
    route = respx.post(f"{BASE}/chat/completions").mock(
        return_value=completion(
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_9",
                        "type": "function",
                        "function": {"name": "cala_search", "arguments": '{"name": "GREÏ"}'},
                    }
                ],
            }
        )
    )
    seen: list[str] = []

    result = await make_llm().chat(
        system="rules",
        messages=[
            Message(role="user", text="Who backs GREÏ?"),
            Message(role="model", tool_calls=[ToolCall(name="cala_search", args={"q": 1})]),
            Message(
                role="user",
                text="Round 1 of 4.",
                tool_results=[ToolResult(name="cala_search", output="GREÏ [Company]")],
            ),
        ],
        tools=[ToolSpec(name="cala_search", description="d", parameters={"type": "object"})],
        on_text=seen.append,
    )

    assert result.tool_calls == [ToolCall(name="cala_search", args={"name": "GREÏ"}, id="call_9")]
    assert seen == []  # no text, nothing streamed
    body = json.loads(route.calls.last.request.content)
    assert body["model"] == "big"
    assert body["tools"][0]["function"]["name"] == "cala_search"
    system, user, assistant, tool, note = body["messages"]
    assert system == {"role": "system", "content": "rules"}
    assert user == {"role": "user", "content": "Who backs GREÏ?"}
    call_id = assistant["tool_calls"][0]["id"]
    # A call that came without an id (Gemini, scripts) still pairs with its result.
    assert tool == {"role": "tool", "tool_call_id": call_id, "content": "GREÏ [Company]"}
    assert note == {"role": "user", "content": "Round 1 of 4."}
    assert route.calls.last.request.headers["authorization"] == "Bearer k"


@respx.mock
async def test_a_text_answer_reaches_on_text():
    respx.post(f"{BASE}/chat/completions").mock(return_value=completion({"content": "Hi. "}))
    seen: list[str] = []

    result = await make_llm().chat(
        system="s", messages=[Message(role="user", text="hi")], on_text=seen.append
    )

    assert (result.text, seen) == ("Hi.", ["Hi."])


@respx.mock
async def test_generate_asks_for_json_on_the_lite_model_and_retries_once_on_bad_json():
    route = respx.post(f"{BASE}/chat/completions").mock(
        side_effect=[
            completion({"content": '{"nope": 1}'}),
            completion({"content": '{"rewrite": true, "reason": "shorter"}'}),
        ]
    )

    verdict = await make_llm().generate(
        task="learn", system="s", prompt="p", schema=Verdict, lite=True
    )

    assert verdict == Verdict(rewrite=True, reason="shorter")
    first = json.loads(route.calls[0].request.content)
    assert first["model"] == "small"
    assert first["response_format"] == {"type": "json_object"}
    assert '"rewrite"' in first["messages"][0]["content"]  # the schema is in the prompt
    assert (
        "did not validate" in json.loads(route.calls[1].request.content)["messages"][-1]["content"]
    )


@respx.mock
async def test_generate_gives_up_after_two_bad_answers():
    respx.post(f"{BASE}/chat/completions").mock(return_value=completion({"content": "{}"}))

    with pytest.raises(LLMError):
        await make_llm().generate(task="learn", system="s", prompt="p", schema=Verdict)


@respx.mock
async def test_a_rate_limit_fails_at_once_so_the_chain_moves_on():
    route = respx.post(f"{BASE}/chat/completions").mock(return_value=httpx.Response(429))

    with pytest.raises(LLMError, match="429"):
        await make_llm().chat(system="s", messages=[Message(role="user", text="hi")])
    assert route.call_count == 1


@respx.mock
async def test_a_server_error_is_retried_once(monkeypatch):
    monkeypatch.setattr("app.llm.openai_compat.asyncio.sleep", _no_sleep)
    respx.post(f"{BASE}/chat/completions").mock(
        side_effect=[httpx.Response(503), completion({"content": "ok"})]
    )

    result = await make_llm().chat(system="s", messages=[Message(role="user", text="hi")])

    assert result.text == "ok"


@respx.mock
async def test_transcribe_sends_the_recording_to_whisper():
    route = respx.post(f"{BASE}/audio/transcriptions").mock(
        return_value=httpx.Response(200, json={"text": " I trust Y Combinator "})
    )

    text = await make_llm().transcribe(audio=b"abc", mime_type="audio/webm;codecs=opus")

    assert text == "I trust Y Combinator"
    request = route.calls.last.request.content
    assert b'filename="audio.webm"' in request and b"whisper" in request


async def test_live_transcription_is_not_offered():
    with pytest.raises(LLMError):
        await make_llm().live_token()


async def _no_sleep(_: float) -> None:
    return None

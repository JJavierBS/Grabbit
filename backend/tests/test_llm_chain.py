import pytest

from app.config import get_settings
from app.llm import ChatResult, LLMError, Message, get_llm, providers
from app.llm.chain import ChainLLM
from app.llm.fake import FakeLLM

HI = [Message(role="user", text="hi")]


class Stub:
    def __init__(self, name: str, *, fails: bool = False):
        self.name = name
        self.fails = fails
        self.calls = 0

    async def chat(self, **_: object) -> ChatResult:
        self.calls += 1
        if self.fails:
            raise LLMError(f"{self.name}: 429")
        return ChatResult(text=self.name)


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


async def test_the_first_provider_that_answers_wins():
    gemini, groq = Stub("gemini", fails=True), Stub("groq")
    chain = ChainLLM([("gemini", gemini), ("openai", groq)])

    assert (await chain.chat(system="s", messages=HI)).text == "groq"


async def test_a_failing_provider_sits_out_then_comes_back():
    clock = Clock()
    gemini, groq = Stub("gemini", fails=True), Stub("groq")
    chain = ChainLLM([("gemini", gemini), ("openai", groq)], clock=clock, cooldown_s=60)

    await chain.chat(system="s", messages=HI)
    await chain.chat(system="s", messages=HI)
    assert gemini.calls == 1  # not retried while resting

    clock.now = 61
    gemini.fails = False
    assert (await chain.chat(system="s", messages=HI)).text == "gemini"


async def test_the_last_provider_never_rests_and_its_error_is_raised():
    clock = Clock()
    only = Stub("scripted", fails=True)
    chain = ChainLLM([("scripted", only)], clock=clock)

    for _ in range(2):
        with pytest.raises(LLMError):
            await chain.chat(system="s", messages=HI)
    assert only.calls == 2


async def test_live_transcription_failing_is_not_an_outage():
    chain = ChainLLM([("openai", FakeLLM(scripts=[])), ("scripted", FakeLLM(scripts=[]))])

    with pytest.raises(LLMError):
        await chain.live_token()
    # Groq has no Live API; that must not bench it for chat.
    assert chain._down_until == {}


def test_auto_without_keys_is_the_scripted_demo(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "auto")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_COMPAT_API_KEY", "")
    get_settings.cache_clear()
    get_llm.cache_clear()

    assert providers(get_llm()) == ["scripted"]


@pytest.mark.parametrize(
    ("text", "investors"),
    [
        ("I trust Y Combinator and 500 Global", ["Y Combinator", "500 Global"]),
        ("I trust Y Combinator.", ["Y Combinator"]),
    ],
)
async def test_the_scripted_demo_follows_the_guided_path(monkeypatch, text, investors):
    monkeypatch.setenv("LLM_MODE", "scripted")
    get_settings.cache_clear()
    get_llm.cache_clear()

    result = await get_llm().chat(
        system="s", messages=[Message(role="user", text=text)], tools=_profile_tools()
    )

    refs = result.tool_calls[0].args["patch"]["reference_investors"]
    assert [r["name"] for r in refs] == investors


async def test_the_scripted_demo_says_it_is_scripted_for_anything_else(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "scripted")
    get_settings.cache_clear()
    get_llm.cache_clear()

    result = await get_llm().chat(
        system="s",
        messages=[Message(role="user", text="What is the weather in Espoo?")],
        tools=_profile_tools(),
    )

    assert "scripted" in result.text and not result.tool_calls


def _profile_tools():
    from app.agent.tools import TOOL_SPECS

    return TOOL_SPECS


def test_a_deploy_without_keys_walks_the_trust_step_through_the_api(client, monkeypatch):
    monkeypatch.setenv("LLM_MODE", "auto")
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.setenv("OPENAI_COMPAT_API_KEY", "")
    get_settings.cache_clear()
    get_llm.cache_clear()
    headers = {"X-Workspace": "portfolio-visitor"}

    reply = client.post(
        "/api/chat", json={"text": "I trust Y Combinator and 500 Global"}, headers=headers
    ).json()

    assert "From now on: Y Combinator and 500 Global as trusted investors." in reply["text"]
    profile = client.get("/api/profile", headers=headers).json()
    assert [r["name"] for r in profile["reference_investors"]] == ["Y Combinator", "500 Global"]


async def test_a_refused_key_sits_out_for_an_hour_and_leaves_what_can_answer():
    clock = Clock()
    gemini, scripted = Stub("gemini", fails=True), Stub("scripted")
    gemini_error = LLMError("chat: Gemini returned 400", auth=True)

    async def refuse(**_: object) -> ChatResult:
        gemini.calls += 1
        raise gemini_error

    gemini.chat = refuse
    chain = ChainLLM([("gemini", gemini), ("scripted", scripted)], clock=clock)
    assert providers(chain) == ["gemini", "scripted"]

    await chain.chat(system="s", messages=HI)
    # The answers now come from the script: health says so, and the badge shows.
    assert providers(chain) == ["scripted"]
    clock.now = 3599
    await chain.chat(system="s", messages=HI)
    assert gemini.calls == 1
    clock.now = 3601
    assert providers(chain) == ["gemini", "scripted"]


async def test_a_rate_limit_rests_only_a_minute():
    clock = Clock()
    chain = ChainLLM(
        [("gemini", Stub("gemini", fails=True)), ("scripted", Stub("scripted"))], clock=clock
    )

    await chain.chat(system="s", messages=HI)
    clock.now = 61

    assert providers(chain) == ["gemini", "scripted"]

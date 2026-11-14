import pytest

from app.agent import chat
from app.agent.sources import fixture_candidates
from app.llm import ChatResult, LLMError
from app.llm.fake import FakeLLM
from app.store import chat as chat_store
from app.store import profile as profile_store


@pytest.fixture
def candidates():
    return fixture_candidates()


async def _say(text, candidates, now, llm=None, hook=None):
    return await chat.handle_message(
        text, llm=llm or FakeLLM(), candidates=candidates, on_profile_change=hook, now=now
    )


async def test_correction_edits_profile_and_rewrites_instructions(candidates, now, published):
    await _say("hello", candidates, now)
    rebuilt = []

    async def hook(profile):
        rebuilt.append(profile.version)
        return "report-2"

    reply = await _say("Shorter, co-investors first", candidates, now, hook=hook)

    profile = profile_store.current()
    assert profile.version == 2
    assert profile.style.length == "short"
    assert profile.instructions.startswith("Lead with startups where a reference investor")
    assert {c.field for c in reply.profile_changes} == {"style.length", "instructions"}
    assert all(c.version == 2 and c.by == "agent" for c in reply.profile_changes)
    assert reply.text.endswith(
        "From now on: shorter reports; co-investors first, two lines per startup."
    )
    assert rebuilt == [2] and reply.report_id == "report-2"
    assert [kind for kind, _ in published] == ["profile"]


async def test_forbidden_instruction_is_refused_and_nothing_changes(candidates, now):
    await _say("hello", candidates, now)
    reply = await _say("Just tell me which one should I buy", candidates, now)

    assert profile_store.current().version == 1
    assert reply.profile_changes == []
    assert "That decision stays yours" in reply.text
    assert "I can't apply that part: the decision on what to buy stays yours." in reply.text
    assert "From now on" not in reply.text


async def test_reaction_without_instruction_is_learned(candidates, now):
    await _say("hello", candidates, now)
    reply = await _say("this is too long", candidates, now)

    assert profile_store.current().instructions.startswith("Keep each startup to two lines")
    assert [c.field for c in reply.profile_changes] == ["instructions"]
    assert "From now on: two lines per startup." in reply.text


async def test_plain_question_changes_nothing(candidates, now):
    await _say("hello", candidates, now)
    reply = await _say("what is a lead investor?", candidates, now)
    assert reply.profile_changes == [] and profile_store.current().version == 1


async def test_first_turn_appends_onboarding_questions(candidates, now):
    reply = await _say("I invest in B2B software", candidates, now)
    assert "Of the 6 startups that match, 4 are pre-seed or seed" in reply.text
    assert profile_store.current().thesis.startswith("Early-stage B2B software")
    second = await _say("ok", candidates, now)
    assert "Of the 6 startups" not in second.text


async def test_model_failure_keeps_profile_and_says_so(candidates, now):
    class Down(FakeLLM):
        async def chat(self, **_):
            raise LLMError("down")

    reply = await _say("Shorter please", candidates, now, llm=Down())
    assert reply.text == chat.UNAVAILABLE
    assert profile_store.current().version == 1
    assert [m.role for m in chat_store.all_messages()] == ["user", "agent"]


async def test_tool_only_answer_gets_a_followup_sentence(candidates, now):
    class ToolsOnly(FakeLLM):
        async def chat(self, *, system, messages, tools=None):
            if tools:
                return ChatResult(
                    tool_calls=[
                        {
                            "name": "update_profile",
                            "args": {"patch": {"cadence": "daily"}, "reason": "a daily digest"},
                        }
                    ]
                )
            return ChatResult(text="Switched to daily.")

    await _say("hello", candidates, now)
    reply = await _say("make it daily", candidates, now, llm=ToolsOnly())
    assert reply.text == "Switched to daily.\n\nFrom now on: a daily digest."


async def test_system_prompt_carries_rules_profile_and_instructions(candidates, now):
    profile = profile_store.current(now).model_copy(update={"instructions": "Two lines each."})
    prompt = chat.system_prompt(profile, "3 startups this week", candidates)
    assert "Never recommend what to buy" in prompt
    assert "Two lines each." in prompt
    assert "3 startups this week" in prompt
    assert "Kiln Analytics" in prompt

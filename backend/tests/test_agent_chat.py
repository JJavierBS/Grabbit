import asyncio

import pytest

from app.agent import chat
from app.agent.sources import fixture_candidates
from app.agent.visual import Visual
from app.llm import ChatResult, LLMError
from app.llm.fake import FakeLLM, Script
from app.models import ChatMessage, ExploredGraph, GraphNode, WalkStep, WalkSummary
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
    published.clear()
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
    # Reading, then the saved profile, then the report rewrite it triggers.
    assert [kind for kind, _ in published] == ["progress", "profile", "progress"]


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


async def test_first_turn_asks_onboarding_questions_with_clickable_answers(candidates, now):
    reply = await _say("I invest in B2B software", candidates, now)
    # Asked as a form under the reply (#153), not as bullets in its text.
    assert "Of the 6 startups" not in reply.text
    stage = next(q for q in reply.questions if q.key == "stage")
    assert stage.text.startswith("Of the 6 startups that match, 4 are pre-seed or seed")
    assert [(o.label, o.answer) for o in stage.options][0] == (
        "Pre-seed and seed",
        "Only pre-seed and seed startups.",
    )
    assert all(q.options for q in reply.questions)
    assert chat_store.all_messages()[-1].questions == reply.questions
    assert profile_store.current().thesis.startswith("Early-stage B2B software")
    second = await _say("ok", candidates, now)
    assert second.questions == []


async def test_the_agent_still_sees_the_questions_it_asked(candidates, now):
    seen = []

    class Recording(FakeLLM):
        async def chat(self, *, system, messages, tools=None, on_text=None):
            seen.append(messages)
            return await super().chat(system=system, messages=messages, tools=tools)

    llm = Recording()
    first = await _say("I invest in B2B software", candidates, now, llm=llm)
    seen.clear()
    await _say("Only pre-seed and seed startups.", candidates, now, llm=llm)
    model_turns = [m.text for call in seen for m in call if m.role == "model"]
    assert any(all(q.text in t for q in first.questions) for t in model_turns)


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
        async def chat(self, *, system, messages, tools=None, on_text=None):
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


async def test_system_prompt_gives_every_fact_a_card_shows(candidates, now):
    """#147: without them the agent called founding dates "not published"."""
    import json

    prompt = chat.system_prompt(profile_store.current(now), None, candidates)
    kiln = next(c for c in candidates if c.name == "Kiln Analytics")
    line = next(json.loads(row) for row in prompt.splitlines() if '"Kiln Analytics"' in row)
    assert line["founded"] == kiln.founding_date.value
    assert line["total_raised"] == {
        "amount": kiln.total_funding.value,
        "unit": kiln.total_funding.unit,
    }
    assert line["description"]
    assert kiln.founding_date.value is not None and kiln.total_funding.value is not None


async def test_turn_with_a_tool_call_skips_learning(candidates, now):
    llm = FakeLLM()
    await _say("hello", candidates, now, llm=llm)
    llm.calls.clear()
    await _say("No B2C please", candidates, now, llm=llm)
    assert [task for task, _ in llm.calls] == ["chat"]


async def test_note_joins_reasons_without_their_full_stops(candidates, now):
    class TwoChanges(FakeLLM):
        async def chat(self, *, system, messages, tools=None, on_text=None):
            if tools:
                return ChatResult(
                    tool_calls=[
                        {
                            "name": "update_profile",
                            "args": {"patch": {"cadence": "daily"}, "reason": "a daily digest."},
                        },
                        {
                            "name": "update_profile",
                            "args": {
                                "patch": {"alert_threshold": "high"},
                                "reason": "fewer alerts.",
                            },
                        },
                    ]
                )
            return ChatResult(text="Done.")

    await _say("hello", candidates, now)
    reply = await _say("daily, fewer alerts", candidates, now, llm=TwoChanges())
    assert reply.text.endswith("From now on: a daily digest; fewer alerts.")


async def test_a_question_gets_a_visual_answer_and_a_correction_does_not(
    candidates, now, monkeypatch
):
    drawn = 'root = Answer([t])\nt = Text("Aurora led it.")'

    async def visual(llm, question, profile, candidates):
        return Visual(ui=drawn)

    monkeypatch.setattr(chat, "visual_answer", visual)
    await _say("hello", candidates, now)

    question = await _say("Who backs Mossa?", candidates, now)
    correction = await _say("Shorter, co-investors first", candidates, now)

    assert question.ui == drawn
    assert correction.profile_changes and correction.ui is None


async def test_the_walked_graph_is_stored_with_the_answer(candidates, now, monkeypatch):
    graph = ExploredGraph(
        nodes=[GraphNode(entity_id="i-1", name="Aurora", entity_type="Organization")],
        edges=[],
    )

    async def visual(llm, question, profile, candidates):
        return Visual(ui='root = Answer([t])\nt = Text("Aurora.")', graph=graph)

    monkeypatch.setattr(chat, "visual_answer", visual)
    await _say("hello", candidates, now)
    reply = await _say("What else did Aurora back?", candidates, now)

    assert reply.graph == graph
    assert chat_store.all_messages()[-1].graph == graph


async def test_a_turn_reports_each_phase_it_enters_in_order(
    candidates, now, monkeypatch, published
):
    started = asyncio.Event()

    async def slow_visual(llm, question, profile, candidates):
        await started.wait()
        return Visual(ui='root = Answer([t])\nt = Text("Aurora.")')

    monkeypatch.setattr(chat, "visual_answer", slow_visual)
    await _say("hello", candidates, now)
    published.clear()

    async def release_visual_soon():
        await asyncio.sleep(0)
        started.set()

    asyncio.get_running_loop().create_task(release_visual_soon())
    await _say("Who backs Mossa?", candidates, now)

    progress = [payload for kind, payload in published if kind == "progress"]
    assert [p.phase for p in progress] == ["llm", "graph"]
    assert all(p.label for p in progress)


async def test_a_correction_skips_the_graph_phase(candidates, now, published):
    await _say("hello", candidates, now)
    published.clear()

    async def hook(profile):
        return "report-2"

    await _say("Shorter, co-investors first", candidates, now, hook=hook)
    assert [p.phase for kind, p in published if kind == "progress"] == ["llm", "report"]


async def test_how_the_walk_found_the_answer_is_stored_with_it(candidates, now, monkeypatch):
    walk = WalkSummary(
        steps=[WalkStep(id=0, kind="search", text="Searching Cala for “Aurora”", done=True)],
        checked=4,
        seconds=3.2,
    )

    async def visual(llm, question, profile, candidates):
        return Visual(ui='root = Answer([t])\nt = Text("Aurora.")', walk=walk)

    monkeypatch.setattr(chat, "visual_answer", visual)
    await _say("hello", candidates, now)
    reply = await _say("What else did Aurora back?", candidates, now)

    assert reply.walk == walk
    assert chat_store.all_messages()[-1].walk == walk


def test_messages_stored_before_the_walk_summary_still_load():
    old = (
        '{"id": "m1", "role": "agent", "text": "Hi.", "created_at": "2026-11-14T10:00:00Z",'
        ' "profile_changes": [], "report_id": null, "ui": null, "graph": null}'
    )
    assert ChatMessage.model_validate_json(old).walk is None


async def test_a_prose_reply_carries_the_sources_of_the_startups_it_names(candidates, now):
    llm = FakeLLM()
    name = candidates[0].name
    llm.scripts.insert(0, Script(task="chat", match=["what about"], text=f"{name} fits."))
    await _say("hello", candidates, now, llm=llm)
    reply = await _say("What about the first one?", candidates, now, llm=llm)

    assert [s.entity_id for s in reply.sources] == [candidates[0].entity_id]
    assert reply.sources[0].sources
    assert chat_store.all_messages()[-1].sources == reply.sources


async def test_a_visual_answer_keeps_its_own_badges_and_cites_nothing_more(
    candidates, now, monkeypatch
):
    async def visual(llm, question, profile, candidates):
        return Visual(ui='root = Answer([t])\nt = Text("Aurora.")')

    monkeypatch.setattr(chat, "visual_answer", visual)
    await _say("hello", candidates, now)
    reply = await _say(f"Tell me about {candidates[0].name}", candidates, now)
    assert reply.sources == []


async def test_the_first_turn_asks_the_questions_the_model_worded(candidates, now):
    """#165: worded for this investor while the report is built."""
    from app.llm.fake import load_scripts

    worded = {
        "key": "stage",
        "text": "De las 6 startups, 4 son pre-semilla o semilla y 2 Serie A o más. ¿Qué etapa?",
        "options": [
            {"label": "Pre-semilla y semilla", "answer": "Solo pre-semilla y semilla."},
            {"label": "Serie A o más", "answer": "Solo Serie A o más."},
            {"label": "Cualquiera", "answer": "Cualquier etapa."},
        ],
    }
    llm = FakeLLM([*load_scripts(), Script(task="questions", output={"questions": [worded]})])

    reply = await _say("Invierto en software B2B", candidates, now, llm=llm)

    assert [q.key for q in reply.questions] == ["stage"]
    assert reply.questions[0].text == worded["text"]
    assert reply.questions[0].options[2].answer == "Cualquier etapa."

import pytest

from app.agent import chat
from app.agent.sources import fixture_candidates
from app.llm import ChatResult
from app.llm.fake import FakeLLM, Script
from app.models import Fact, Profile, Signal
from app.reports.build import build
from app.reports.rank import rank
from app.store.profile import default_profile


def profile(now, **changes):
    data = default_profile(now).model_dump()
    for key, fields in changes.items():
        data[key].update(fields)
    return Profile.model_validate(data)


async def test_an_explicit_limit_controls_cards_and_prose(now):
    p = profile(now, style={"max_candidates": 3})
    report = await build("prep", llm=FakeLLM(), profile=p, candidates=fixture_candidates(), now=now)
    assert len(report.candidates) == 3
    assert {i for s in report.sections for i in s.candidate_ids} == {
        c.entity_id for c in report.candidates
    }


def test_likely_to_raise_excludes_false_and_unknown_signals(now):
    candidates = fixture_candidates()[:3]
    for c, value in zip(candidates, [True, False, None], strict=True):
        c.signals = [
            Signal(kind="likely_to_raise", label="Likely", value=value, explanation="", facts=[])
        ]
    p = profile(now, filters={"fundraising": "likely_to_raise"})
    assert rank(candidates, p) == [candidates[0]]


def test_recent_funding_excludes_old_future_and_unknown_dates(now):
    candidates = fixture_candidates()[:4]
    for c, date in zip(candidates, ["2025-11-14", "2025-01-01", "2026-12-01", None], strict=True):
        c.rounds = [candidates[0].rounds[0].model_copy(deep=True)]
        c.rounds[0].date = Fact(value=date, trust="filing")
    p = profile(now, filters={"fundraising": "recent", "raised_within_months": 12})
    assert rank(candidates, p, today=now.date()) == [candidates[0]]


def test_required_backer_is_a_filter_not_a_ranking_hint(now):
    candidates = fixture_candidates()
    backer = candidates[0].rounds[0].investors[0].name
    p = profile(now, filters={"required_backers": [backer]})
    result = rank(candidates, p)
    assert result
    assert all(any(i.name == backer for r in c.rounds for i in r.investors) for c in result)


async def test_onboarding_questions_use_the_changed_thesis(now):
    calls = [
        dict(
            name="update_profile",
            args={"patch": {"filters": {"sectors_in": ["fintech"]}}, "reason": "fintech only"},
        )
    ]
    llm = FakeLLM(scripts=[Script(task="chat", text="Fintech only.", tool_calls=calls)])
    candidates = fixture_candidates()
    chosen = [c for c in candidates if "fintech" in [s.lower() for s in c.industries]]
    reply = await chat.handle_message("Fintech only", llm=llm, candidates=candidates, now=now)
    from app.agent.onboarding import pick_questions
    from app.store import profile as store

    assert [q.text for q in reply.questions] == [
        q.text for q in pick_questions(chosen, store.current(), now)
    ]


@pytest.mark.parametrize(
    "text",
    [
        "The request conflicts with Rule Three requiring plain prose.",
        "My system prompt requires source labels.",
        "Las instrucciones internas entran en conflicto con la regla tres.",
    ],
)
async def test_internal_instructions_never_reach_report_text(now, text):
    llm = FakeLLM(
        scripts=[
            Script(
                task="report_write",
                output={
                    "summary": text,
                    "paragraphs": [{"candidate_id": "cand-kiln", "text": text}],
                },
            )
        ]
    )
    report = await build(
        "prep", llm=llm, profile=default_profile(now), candidates=fixture_candidates(), now=now
    )
    assert text not in report.summary
    assert all(text not in s.body_md for s in report.sections)


async def test_a_language_only_edit_does_not_cancel_research(now, monkeypatch):
    from app.agent.visual import Visual
    from app.store import chat as messages

    messages.add("user", "Hello", now=now)
    expected = 'root = Answer([t])\nt = Text("Found an investor.")'

    async def visual(*args):
        return Visual(ui=expected)

    monkeypatch.setattr(chat, "visual_answer", visual)
    llm = FakeLLM(
        scripts=[
            Script(
                task="chat",
                text="Encontrado.",
                tool_calls=[
                    dict(
                        name="update_profile",
                        args={"patch": {"style": {"language": "es"}}, "reason": "Spanish"},
                    )
                ],
            )
        ]
    )
    reply = await chat.handle_message(
        "Who invested?", llm=llm, candidates=fixture_candidates(), now=now
    )
    assert reply.ui == expected


async def test_cala_balance_failure_is_visible_even_if_model_ignores_it(now):
    from contextlib import asynccontextmanager

    from app.agent.explore import walk
    from app.cala.client import CalaError

    class EmptyBalance:
        async def search(self, *args, **kwargs):
            raise CalaError(402, "Insufficient balance")

    @asynccontextmanager
    async def client():
        yield EmptyBalance()

    llm = FakeLLM(
        scripts=[
            Script(task="explore", tool_calls=[dict(name="cala_search", args={"name": "YC"})]),
            Script(task="chat", text="Nothing found."),
        ]
    )
    text, graph = await walk(
        llm, system="", question="Who invested?", open_client=client, trusted=set()
    )
    assert "balance" in text and "No new connections" in text
    assert graph is None


async def test_explored_headcount_uses_a_range():
    from contextlib import asynccontextmanager

    from app.agent.explore import Walk
    from app.llm import ToolCall

    class Client:
        async def introspect(self, *args):
            return {"properties": ["employee_count_range"]}

        async def retrieve(self, entity_id, *args):
            return {
                "id": entity_id,
                "name": "Slicker",
                "entity_type": "Company",
                "properties": {"employee_count_range": {"value": [1, 11], "sources": []}},
            }

    @asynccontextmanager
    async def client():
        yield Client()

    async with Walk(client, set()) as state:
        await state.run(ToolCall(name="cala_neighbours", args={"entity_ids": ["slicker"]}))
        assert state.graph().nodes[0].facts["employee_count_range"].value == "1-11"


async def test_graph_research_is_available_with_an_empty_shortlist(now):
    from contextlib import asynccontextmanager

    from app.agent.visual import visual_answer
    from app.store.profile import default_profile
    from tests.test_agent_explore import FIRSTPICK, Recording, call

    class Client:
        async def search(self, *args, **kwargs):
            return [{"id": FIRSTPICK, "name": "FIRSTPICK", "entity_type": "Company"}]

    @asynccontextmanager
    async def client():
        yield Client()

    llm = Recording(
        [
            ChatResult(tool_calls=[call("cala_search", name="FIRSTPICK")]),
            ChatResult(text='root = Answer([t])\nt = Text("Found FIRSTPICK.")'),
        ]
    )
    result = await visual_answer(
        llm, "Find FIRSTPICK", default_profile(now), [], open_client=client
    )
    assert result is not None


def test_country_question_never_uses_a_street_address(now):
    from app.agent.onboarding import pick_questions

    candidates = fixture_candidates()[:2]
    candidates[0].hq.value = "Bändliweg 20, 8048 Zürich, Switzerland"
    candidates[1].hq.value = "London, United Kingdom"
    p = default_profile(now)
    question = next(q for q in pick_questions(candidates, p, now, limit=10) if q.key == "hq")
    assert "Bändliweg" not in question.text
    assert any("Switzerland" in answer for _, answer in question.options)

"""The chat agent walking Cala's graph (#73), on recorded Cala responses and scripted LLMs."""

import json
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import pytest

from app.agent import explore
from app.agent.explore import TOOLS, walk
from app.agent.sources import fixture_candidates
from app.agent.visual import PROMPT, visual_answer
from app.cala.client import CalaClient
from app.llm import ChatResult, ToolCall
from app.llm.fake import FakeLLM, Script
from app.models import ReferenceInvestor
from app.store import profile as profile_store
from app.store.cala_cache import CalaCache, cache_key
from tests.conftest import FIXTURES

FIRSTPICK = "88b67750-caa3-40ca-bfde-8eb88aa48ae4"
GREI_PRESEED = "3dba66dc-5eec-5c0d-96cb-60e88365ef65"
REBOOKIFY_PRESEED = "ae44bd34-20a9-586d-8796-b12981dfcd8d"
GREI = "0094ec10-bd61-4833-bf19-c2ab9d78312b"
GLOBAL_500 = "7e55b310-361b-4b08-952d-98fcd8f2ab49"

PROFILE = profile_store.default_profile(datetime(2026, 11, 14, tzinfo=UTC)).model_copy(
    update={
        "reference_investors": [
            ReferenceInvestor(entity_id=GLOBAL_500, name="500 Global (500 Emerging Europe)")
        ]
    }
)
ANSWER = (
    "root = Answer([t, g, f])\n"
    't = Text("FIRSTPICK led the pre-seed of GREÏ and joined Rebookify with 500 Global.")\n'
    f'g = ExploredGraph("{FIRSTPICK}")\n'
    f'f = EntityFacts("{GREI_PRESEED}")'
)


def call(tool, **args):
    return ToolCall(name=tool, args=args)


# Most specific first: FakeLLM answers with the first script whose match is in the last turn.
WALK_SCRIPTS = [
    Script(task="explore", match=["Rebookify [Company"], text=ANSWER),
    Script(
        task="explore",
        match=["do not carry the company"],
        tool_calls=[call("cala_neighbours", entity_ids=[GREI_PRESEED, REBOOKIFY_PRESEED])],
    ),
    Script(
        task="explore",
        match=["Search 'FIRSTPICK'"],
        tool_calls=[call("cala_neighbours", entity_ids=[FIRSTPICK])],
    ),
    Script(task="explore", match=["firstpick"], tool_calls=[call("cala_search", name="FIRSTPICK")]),
]


@pytest.fixture
def recorded(conn):
    """A replay-mode Cala client holding only the recorded FIRSTPICK walk."""
    cache = CalaCache(conn)
    for r in json.loads((FIXTURES / "cala" / "real_walk_firstpick.json").read_text()):
        key = cache_key(r["method"], r["path"], r["params"], r["body"])
        cache.put(
            key, r["method"], r["path"], {"params": r["params"], "body": r["body"]}, r["response"]
        )
    client = CalaClient(None, cache, mode="replay")

    @asynccontextmanager
    async def open_client():
        yield client

    return open_client


async def test_a_question_beyond_the_report_walks_cala_and_draws_what_it_found(recorded):
    llm = FakeLLM(WALK_SCRIPTS)

    visual = await visual_answer(
        llm, "Who did FIRSTPICK back?", PROFILE, fixture_candidates(), open_client=recorded
    )

    assert visual is not None and visual.ui == ANSWER
    graph = visual.graph
    nodes = {n.entity_id: n for n in graph.nodes}
    assert {FIRSTPICK, GREI_PRESEED, GREI, GLOBAL_500} <= set(nodes)
    assert len(nodes) <= explore.MAX_NODES
    edges = {(e.source, e.target): e for e in graph.edges}
    lead = edges[(FIRSTPICK, GREI_PRESEED)]
    assert (lead.relationship, lead.role, lead.is_lead) == (
        "PARTICIPATES_IN_FUNDING_ROUND",
        "INVESTOR",
        True,
    )
    assert edges[(GREI, GREI_PRESEED)].role == "ISSUER"
    # Values come from Cala with their trust level, never from the model.
    amount = nodes[GREI_PRESEED].facts["transaction_value"]
    assert (amount.value, amount.unit, amount.trust) == (650000.0, "EUR", "press")
    assert nodes[GREI].facts == {}  # reached, not expanded


class Recording:
    """Scripted LLM that records whether each call offered the Cala tools."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.offered = []
        self.last = []

    async def chat(self, *, system, messages, tools=None):
        self.offered.append(tools is not None)
        self.last.append(messages[-1])
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]


async def test_the_walk_stops_after_the_round_budget_and_asks_for_an_answer(recorded):
    search = ChatResult(tool_calls=[call("cala_search", name="FIRSTPICK")])
    llm = Recording([search] * explore.MAX_ROUNDS + [ChatResult(text="NONE")])

    text, _ = await walk(llm, system="", question="q", open_client=recorded, trusted=set())

    assert text == "NONE"
    assert llm.offered == [True] * explore.MAX_ROUNDS + [False]
    assert "budget is used up" in llm.last[-1].text


async def test_one_round_answers_every_call_and_runs_at_most_three(recorded):
    calls = [call("cala_search", name="FIRSTPICK")] * 4 + [call("update_profile")]
    llm = Recording([ChatResult(tool_calls=calls), ChatResult(text="NONE")])

    await walk(llm, system="", question="q", open_client=recorded, trusted=set())

    results = llm.last[-1].tool_results
    assert len(results) == 5
    assert results[3].output.startswith("Skipped") and results[4].output.startswith("Unknown")


async def test_the_entity_budget_caps_the_graph(recorded, monkeypatch):
    monkeypatch.setattr(explore, "MAX_NODES", 4)
    llm = Recording(
        [ChatResult(tool_calls=[call("cala_neighbours", entity_ids=[FIRSTPICK])]), ChatResult()]
    )

    _, graph = await walk(llm, system="", question="q", open_client=recorded, trusted=set())

    assert len(graph.nodes) == 4
    assert "budget" in llm.last[-1].text


async def test_hub_nodes_are_not_expanded(recorded):
    walk_state = explore.Walk(recorded, set())
    walk_state.seen_types["slush"] = "Event"
    out = await walk_state.run(call("cala_neighbours", entity_ids=["slush"]))
    assert "hub node" in out and walk_state.cala_calls == 0


async def test_replay_without_the_walk_cached_degrades_to_the_report(conn):
    client = CalaClient(None, CalaCache(conn), mode="replay")

    @asynccontextmanager
    async def empty():
        yield client

    report_only = 'root = Answer([t, g])\nt = Text("Mossa fits.")\ng = CompanyGraph("cand-mossa")'
    llm = Recording(
        [
            ChatResult(tool_calls=[call("cala_search", name="Y Combinator")]),
            ChatResult(text=report_only),
        ]
    )

    visual = await visual_answer(
        llm, "What else did YC back?", PROFILE, fixture_candidates(), open_client=empty
    )

    assert visual.ui == report_only and visual.graph is None
    assert llm.offered == [True, False]
    assert "unavailable" in llm.last[-1].text


async def test_an_answer_drawing_a_walk_that_never_happened_is_dropped(conn):
    @asynccontextmanager
    async def empty():
        yield CalaClient(None, CalaCache(conn), mode="replay")

    ui = 'root = Answer([t, g])\nt = Text("Here.")\ng = ExploredGraph("x")'
    visual = await visual_answer(
        Recording([ChatResult(text=ui)]), "q", PROFILE, fixture_candidates(), open_client=empty
    )
    assert visual is None


async def test_a_number_in_text_gets_one_rewrite_then_is_dropped(recorded):
    digits = 'root = Answer([t])\nt = Text("It raised 650k in 2025.")'
    clean = 'root = Answer([t])\nt = Text("500 Global joined it.")'

    fixed = Recording([ChatResult(text=digits), ChatResult(text=clean)])
    visual = await visual_answer(fixed, "q", PROFILE, fixture_candidates(), open_client=recorded)
    assert visual.ui == clean  # a fund name with digits is not a value
    assert "number" in fixed.last[-1].text and fixed.offered == [True, False]

    stubborn = Recording([ChatResult(text=digits)])
    assert (
        await visual_answer(stubborn, "q", PROFILE, fixture_candidates(), open_client=recorded)
        is None
    )


async def test_fake_mode_explores_nothing_by_default(recorded):
    visual = await visual_answer(
        FakeLLM(), "Who did FIRSTPICK back?", PROFILE, fixture_candidates(), open_client=recorded
    )
    assert visual is None


def test_the_tools_offer_search_and_neighbours():
    assert [t.name for t in TOOLS] == ["cala_search", "cala_neighbours"]


def test_entity_facts_offers_every_property_the_walk_keeps():
    # EXPLORED_FIELDS in frontend/src/features/chat/openui/facts.ts must follow KEY_PROPERTIES.
    signature = next(line for line in PROMPT.splitlines() if line.startswith("EntityFacts("))
    assert all(f'"{p}"' in signature for p in explore.KEY_PROPERTIES)

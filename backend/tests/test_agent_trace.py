"""The live Cala walk shown in the chat (#134): steps, growing graph, streamed answer."""

import asyncio

from app.agent import explore
from app.agent.progress import report_attendees
from app.agent.sources import fixture_candidates
from app.agent.trace import Tracer
from app.agent.visual import visual_answer
from app.llm import ChatResult, ToolCall
from app.llm.fake import FakeLLM
from app.models import ExploredGraph, GraphEdge, GraphNode, WalkTrace
from tests.test_agent_explore import (  # noqa: F401  `recorded` is a fixture
    ANSWER,
    FIRSTPICK,
    PROFILE,
    WALK_SCRIPTS,
    Recording,
    recorded,
)


def traces(published) -> list[WalkTrace]:
    return [payload for kind, payload in published if kind == "trace"]


async def test_the_walk_publishes_each_step_the_growing_graph_and_the_streamed_answer(
    recorded,  # noqa: F811
    published,
):
    visual = await visual_answer(
        FakeLLM(WALK_SCRIPTS),
        "Who did FIRSTPICK back?",
        PROFILE,
        fixture_candidates(),
        open_client=recorded,
    )
    seen = traces(published)

    assert len({t.turn for t in seen}) == 1
    last = seen[-1]
    assert last.done and not last.streaming and last.answer == visual.ui == ANSWER
    assert [(s.kind, s.done) for s in last.steps] == [
        ("search", True),
        ("expand", True),
        ("expand", True),
    ]
    # Plain words, no graph jargon (#138): what was found, counted the way people count.
    assert [(s.text, s.result) for s in last.steps] == [
        ("Searching Cala for “FIRSTPICK”", "found FIRSTPICK"),
        ("Looking at FIRSTPICK’s funding rounds and people", "found 6 funding rounds"),
        (
            "Opening 2 funding rounds to see who raised and who invested",
            "found 2 startups and 2 investors, including 500 Global, whom you trust",
        ),
    ]
    assert last.root_id == FIRSTPICK and last.round == 3
    assert last.max_rounds == explore.MAX_ROUNDS and last.max_nodes == explore.MAX_NODES
    # The graph only grows, and the final one is the one stored with the answer.
    sizes = [len(t.graph.nodes) for t in seen if t.graph]
    assert sizes == sorted(sizes) and sizes[-1] == len(visual.graph.nodes) == last.nodes
    # The answer streams in before the walk is over.
    partial = [t.answer for t in seen if t.streaming]
    assert partial and partial[0] != ANSWER and ANSWER.startswith(partial[0])


async def test_a_step_starts_before_cala_answers_and_ends_after(recorded, published):  # noqa: F811
    await visual_answer(
        FakeLLM(WALK_SCRIPTS),
        "Who did FIRSTPICK back?",
        PROFILE,
        fixture_candidates(),
        open_client=recorded,
    )
    first = [t.steps[0] for t in traces(published) if t.steps]
    assert not first[0].done and first[0].result is None
    assert first[-1].done and first[-1].result


async def test_a_rewritten_answer_shows_as_its_own_step(recorded, published):  # noqa: F811
    digits = 'root = Answer([t])\nt = Text("It raised 650k in 2025.")'
    clean = 'root = Answer([t])\nt = Text("500 Global joined it.")'

    await visual_answer(
        Recording([ChatResult(text=digits), ChatResult(text=clean)]),
        "q",
        PROFILE,
        fixture_candidates(),
        open_client=recorded,
    )
    last = traces(published)[-1]
    assert [s.kind for s in last.steps] == ["rewrite"]
    assert last.steps[0].text == "Rewriting the answer so every number comes from Cala"
    assert last.answer == clean


async def test_a_dropped_answer_closes_the_walk_without_one(recorded, published):  # noqa: F811
    await visual_answer(
        Recording([ChatResult(text="NONE")]),
        "q",
        PROFILE,
        fixture_candidates(),
        open_client=recorded,
    )
    last = traces(published)[-1]
    assert last.done and last.answer is None


async def test_prose_before_tool_calls_is_not_streamed_as_an_answer(published):
    tracer = Tracer(max_rounds=6, max_nodes=30)
    tracer.answer("Let me look that up in Cala.")
    assert traces(published) == []
    tracer.answer("```openui\nroot = Answer([t])")
    assert traces(published)[-1].answer == "root = Answer([t])"
    tracer.drop_answer()
    assert traces(published)[-1].answer is None and not traces(published)[-1].streaming


async def test_a_cancelled_walk_still_closes(recorded, published):  # noqa: F811
    started = asyncio.Event()

    class Slow:
        async def chat(self, **_):
            started.set()
            await asyncio.sleep(10)

    task = asyncio.create_task(
        visual_answer(Slow(), "q", PROFILE, fixture_candidates(), open_client=recorded)
    )
    await started.wait()
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert traces(published)[-1].done


async def test_demo_pacing_holds_a_fast_step_on_screen_and_never_a_slow_one(published):
    now = [0.0]
    slept: list[float] = []

    async def sleep(s: float) -> None:
        slept.append(s)

    tracer = Tracer(max_rounds=6, max_nodes=30, min_step_s=0.6, clock=lambda: now[0], sleep=sleep)
    fast = tracer.start("search", "Searching Cala for “A”")
    now[0] = 0.1
    await tracer.finish(fast, "1 match")
    slow = tracer.start("expand", "Expanding A")
    now[0] = 2.0
    await tracer.finish(slow, "+3 entities, +3 links")

    assert slept == [0.5]
    # Pacing adds no step of its own.
    assert [s.text for s in traces(published)[-1].steps] == [
        "Searching Cala for “A”",
        "Expanding A",
    ]


async def test_thoughts_show_as_one_trimmed_step(published):
    tracer = Tracer(max_rounds=6, max_nodes=30)
    tracer.thought("I need the fund first.\n\n" + "word " * 200)
    step = traces(published)[-1].steps[0]
    assert step.kind == "thought" and step.done
    assert len(step.text) <= 280 and step.text.endswith("…") and "\n" not in step.text


async def test_a_titled_thought_shows_only_its_titles(published):
    tracer = Tracer(max_rounds=6, max_nodes=30)
    tracer.thought("**Analyzing FIRSTPICK's Involvement**\n\nI'm trying to determine " + "x " * 99)
    assert traces(published)[-1].steps[0].text == "Analyzing FIRSTPICK's Involvement"


def test_the_graph_keeps_its_first_root():
    tracer = Tracer(max_rounds=6, max_nodes=30)
    node = GraphNode(entity_id="a", name="A", entity_type="Company")
    tracer.graph(ExploredGraph(nodes=[node], edges=[]), "a")
    tracer.graph(ExploredGraph(nodes=[node], edges=[]), "b")
    assert tracer.state.root_id == "a" and tracer.state.nodes == 1


def test_the_walk_budget_allows_six_rounds():
    assert explore.MAX_ROUNDS == 6 and explore.MAX_NODES == 30 and explore.DEADLINE_S >= 55


def test_attendee_progress_is_counted_every_few_attendees(published):
    for checked in range(1, 13):
        report_attendees(checked, 12, startups=checked // 4)
    progress = [p for kind, p in published if kind == "progress"]
    assert [p.done for p in progress] == [1, 5, 10, 12]
    assert all(p.phase == "cala" and p.total == 12 for p in progress)
    assert progress[-1].label == "Checking Slush attendees in Cala: 12 of 12 · 3 startups so far…"
    assert progress[0].label == "Checking Slush attendees in Cala: 1 of 12…"


def _state(nodes: list[GraphNode], edges: list[GraphEdge], trusted=frozenset()) -> explore.Walk:
    state = explore.Walk(None, set(trusted))
    for n in nodes:
        state.nodes[n.entity_id] = n
        state.seen_types[n.entity_id] = n.entity_type
        state.seen_names[n.entity_id] = n.name
    for e in edges:
        state.edges[(e.source, e.target, e.relationship)] = e
    return state


def _expand(*ids: str) -> ToolCall:
    return ToolCall(name="cala_neighbours", args={"entity_ids": list(ids)})


def test_each_kind_of_entity_is_opened_in_plain_words():
    person = GraphNode(entity_id="p", name="Ada", entity_type="Person")
    company = GraphNode(entity_id="c", name="Mossa", entity_type="Company")
    rnd = GraphNode(entity_id="r", name="Seed", entity_type="FundingRound")
    state = _state([person, company, rnd], [])
    text = explore._step_text

    assert text(_expand("p"), state) == "Looking at what Ada founded and where they work"
    assert text(_expand("c"), state) == "Looking at Mossa’s funding rounds and people"
    assert text(_expand("r"), state) == "Opening a funding round to see who raised and who invested"
    assert text(_expand("c", "r"), state) == "Looking at Mossa and 1 funding round"
    # An id the model took from the report is named from the report, never shown raw.
    named = explore.Walk(None, set(), names={"cand-x": "Kide Health"})
    assert text(_expand("cand-x"), named) == "Looking at Kide Health’s funding rounds and people"
    assert "cand-" not in text(_expand("unknown-id"), named)
    state.seen_names["c"] = "Aurora Ventures"
    assert text(_expand("c"), state) == "Looking at Aurora Ventures’ funding rounds and people"


def test_what_a_step_found_is_counted_by_what_people_call_it():
    founder = GraphNode(entity_id="p", name="Ada", entity_type="Person")
    startup = GraphNode(entity_id="s", name="Mossa", entity_type="Company")
    fund = GraphNode(entity_id="f", name="500 Global (500 Emerging Europe)", entity_type="Company")
    other = GraphNode(entity_id="f2", name="Lifeline", entity_type="Organization")
    rnd = GraphNode(entity_id="r", name="Seed", entity_type="FundingRound")
    edges = [
        GraphEdge(source="p", target="s", relationship="FOUNDED"),
        GraphEdge(source="s", target="r", relationship="RAISED", role="ISSUER"),
        GraphEdge(source="f", target="r", relationship="INVESTS", role="INVESTOR"),
        GraphEdge(source="f2", target="r", relationship="PARTICIPATES_IN_FUNDING_ROUND"),
    ]
    state = _state([founder, startup, fund, other, rnd], edges, trusted={"f"})
    result = explore._step_result(_expand("r"), state, before=set(), output="")
    assert (
        result == "found 1 startup, 2 investors and 1 founder, including 500 Global, whom you trust"
    )


def test_empty_hub_and_failed_steps_say_so_plainly():
    state = _state([], [])
    assert explore._step_result(_expand("x"), state, set(), "x: a hub node") == (
        "too big to open: thousands of connections"
    )
    assert explore._step_result(_expand("x"), state, set(), "") == "nothing new"
    assert explore._step_result(_expand("x"), state, set(), "x: Cala did not answer in time.") == (
        "Cala took too long, moving on"
    )
    search = ToolCall(name="cala_search", args={"name": "Nope"})
    assert explore._step_result(search, state, set(), "") == "nothing by that name"
    state.unavailable = True
    assert explore._step_result(search, state, set(), "") == "Cala is not reachable right now"


async def test_the_answer_keeps_its_walk_without_the_models_reasoning(recorded):  # noqa: F811
    visual = await visual_answer(
        FakeLLM(WALK_SCRIPTS),
        "Who did FIRSTPICK back?",
        PROFILE,
        fixture_candidates(),
        open_client=recorded,
    )
    assert [s.kind for s in visual.walk.steps] == ["search", "expand", "expand"]
    assert all(s.done for s in visual.walk.steps)
    assert visual.walk.checked == len(visual.graph.nodes)


def test_a_walk_without_cala_calls_keeps_no_summary():
    tracer = Tracer(max_rounds=6, max_nodes=30)
    tracer.thought("**Answering from the report**")
    assert tracer.summary() is None


async def test_an_investor_typed_in_chat_is_trusted_in_the_walk(recorded, published):  # noqa: F811
    from app.models import ReferenceInvestor
    from app.references import remember
    from tests.test_agent_explore import GLOBAL_500

    remember({"500 global (500 emerging europe)": GLOBAL_500})
    typed = PROFILE.model_copy(
        update={
            "reference_investors": [
                ReferenceInvestor(entity_id="unresolved:500 Global", name="500 Global")
            ]
        }
    )
    await visual_answer(
        FakeLLM(WALK_SCRIPTS),
        "Who did FIRSTPICK back?",
        typed,
        fixture_candidates(),
        open_client=recorded,
    )
    assert traces(published)[-1].steps[-1].result.endswith("including 500 Global, whom you trust")

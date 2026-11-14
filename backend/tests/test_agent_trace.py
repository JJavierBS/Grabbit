"""The live Cala walk shown in the chat (#134): steps, growing graph, streamed answer."""

import asyncio

from app.agent import explore
from app.agent.progress import report_attendees
from app.agent.sources import fixture_candidates
from app.agent.trace import Tracer
from app.agent.visual import visual_answer
from app.llm import ChatResult
from app.llm.fake import FakeLLM
from app.models import ExploredGraph, GraphNode, WalkTrace
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
    assert last.steps[0].text == "Searching Cala for “FIRSTPICK”"
    assert last.steps[0].result.startswith("1 match") or "matches" in last.steps[0].result
    # The second expansion names the rounds it reached in the first, not their ids.
    assert "entity " not in last.steps[2].text and last.steps[1].result.startswith("+")
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
    assert last.steps[0].text == "Rewriting the answer: a Text holds a number or date"
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
    tracer.thought("**Finding the fund**\n\n" + "word " * 200)
    step = traces(published)[-1].steps[0]
    assert step.kind == "thought" and step.done
    assert len(step.text) <= 280 and step.text.endswith("…") and "\n" not in step.text


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

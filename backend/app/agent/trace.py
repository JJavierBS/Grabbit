"""Shows the open chat the Cala walk as it happens (#134).

Every change (a step starts or ends, the subgraph grows, more of the answer streams in) is
published whole as a `trace` event, so a client that dropped one still draws the latest
state. Steps are the agent's real tool calls in plain words; nothing is timed or invented.
`min_step_s` only holds a real step on screen a little longer, so a walk answered from the
cache in milliseconds can still be followed on a projector.
"""

from __future__ import annotations

import asyncio
import re
import time
import uuid
from collections.abc import Awaitable, Callable

from app import events
from app.models import ExploredGraph, WalkStep, WalkStepKind, WalkSummary, WalkTrace

THOUGHT_CHARS = 280
OPENUI_START = "root ="
# Gemini opens each thought summary with a bold title, e.g. "**Expanding Funding Rounds**".
_TITLE = re.compile(r"\*\*(.+?)\*\*")


class Tracer:
    def __init__(
        self,
        *,
        max_rounds: int,
        max_nodes: int,
        min_step_s: float = 0.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.state = WalkTrace(
            turn=uuid.uuid4().hex[:12],
            round=0,
            max_rounds=max_rounds,
            nodes=0,
            max_nodes=max_nodes,
            steps=[],
        )
        self._min_step_s = min_step_s
        self._clock = clock
        self._sleep = sleep
        self._started: dict[int, float] = {}
        self._opened = clock()

    def publish(self) -> None:
        # A snapshot: the state keeps changing after this event is queued.
        events.publish("trace", self.state.model_copy(deep=True))

    def start(self, kind: WalkStepKind, text: str) -> WalkStep:
        step = WalkStep(id=len(self.state.steps), kind=kind, text=text)
        self.state.steps.append(step)
        self._started[step.id] = self._clock()
        self.publish()
        return step

    async def finish(self, step: WalkStep, result: str | None) -> None:
        held = self._min_step_s - (self._clock() - self._started.pop(step.id, self._clock()))
        if held > 0:
            await self._sleep(held)
        step.result = result
        step.done = True
        self.publish()

    def note(self, kind: WalkStepKind, text: str) -> None:
        """A step that is over as soon as it is shown, e.g. the model's reasoning."""
        self.state.steps.append(WalkStep(id=len(self.state.steps), kind=kind, text=text, done=True))
        self.publish()

    def thought(self, text: str) -> None:
        """The model's own summary, shown by its title when it has one: short enough to read."""
        titles = _TITLE.findall(text)
        text = "; ".join(t.strip() for t in titles) if titles else " ".join(text.split())
        if text:
            cut = text if len(text) <= THOUGHT_CHARS else text[: THOUGHT_CHARS - 1] + "…"
            self.note("thought", cut)

    def round(self, n: int) -> None:
        self.state.round = n
        self.publish()

    def graph(self, graph: ExploredGraph | None, root_id: str | None) -> None:
        self.state.graph = graph
        self.state.nodes = len(graph.nodes) if graph else 0
        self.state.root_id = self.state.root_id or root_id
        self.publish()

    def answer(self, text: str) -> None:
        """More of the answer streamed in. Prose before tool calls is not an answer."""
        ui = text.strip().removeprefix("```openui").removeprefix("```").lstrip()
        if not ui.startswith(OPENUI_START):
            return
        self.state.answer = ui
        self.state.streaming = True
        self.publish()

    def drop_answer(self) -> None:
        if self.state.answer is not None or self.state.streaming:
            self.state.answer = None
            self.state.streaming = False
            self.publish()

    def summary(self) -> WalkSummary | None:
        """The walk to keep on the answer, or None when the agent never called Cala."""
        steps = [s for s in self.state.steps if s.kind != "thought"]
        if not any(s.kind in ("search", "expand") for s in steps):
            return None
        return WalkSummary(
            steps=[s.model_copy() for s in steps],
            checked=self.state.nodes,
            seconds=round(self._clock() - self._opened, 1),
        )

    def close(self, answer: str | None) -> None:
        """The walk is over; `answer` is what the chat will show, or None if it was dropped."""
        self.state.answer = answer
        self.state.streaming = False
        self.state.done = True
        self.publish()

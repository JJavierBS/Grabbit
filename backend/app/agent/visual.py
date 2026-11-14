"""A visual answer in OpenUI Lang, drawn in the chat from Cala data.

The model only picks components and Cala entity ids; the components read every value from
the report or from the subgraph the agent walked in Cala (`explore.py`), so the visual
cannot carry an invented fact. The component library and its prompt live in
`frontend/src/features/chat/openui/`; `openui_prompt.txt` is generated from it (a frontend
test fails when they drift).
"""

import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from app.agent.explore import MAX_NODES, MAX_ROUNDS, ClientFactory, walk
from app.cala.client import CalaClient
from app.llm import LLM, LLMError
from app.models import Candidate, ExploredGraph, Profile

log = logging.getLogger(__name__)

PROMPT = (Path(__file__).parent / "openui_prompt.txt").read_text()
NONE = "NONE"
EXPLORED_COMPONENTS = ("ExploredGraph(", "EntityFacts(")
_TEXT = re.compile(r'Text\("((?:[^"\\]|\\.)*)"\)')


@dataclass
class Visual:
    ui: str
    graph: ExploredGraph | None = None


@asynccontextmanager
async def _shared_cala() -> AsyncIterator[CalaClient]:
    from app.runtime import open_cala

    async with open_cala() as (client, _):
        yield client


def system_prompt(profile: Profile, candidates: list[Candidate]) -> str:
    from app.agent.chat import _candidate_lines  # shared row format

    trusted = (
        ", ".join(f"{r.name} (id {r.entity_id})" for r in profile.reference_investors) or "(none)"
    )
    return f"""{PROMPT}

Investors this angel trusts: {trusted}

Startups in the current report:
{_candidate_lines(candidates)}

How to answer:
- If the report above answers the question, answer at once with the report components and
  no tool call.
- Otherwise walk Cala's graph: cala_search to find an entity by name (pick the hit by type
  and description), then cala_neighbours to expand it and the entities you reach, several
  ids per call. You have {MAX_ROUNDS} tool rounds and {MAX_NODES} entities. Funding rounds
  link a company (role ISSUER) to its investors (role INVESTOR, lead when is_lead).
- Then answer with ExploredGraph(rootId) to draw what you walked, starting from the entity
  the question is about, and at most two EntityFacts for values of entities you expanded.
  If Cala had less than you hoped, still draw what you found and say what is missing in
  Text.
- Values in tool results are for you to choose what to show; never copy a number or date
  into Text.
- Output exactly {NONE} only if the question is not about companies, investors or people
  (for example a request to change the report)."""


async def visual_answer(
    llm: LLM,
    question: str,
    profile: Profile,
    candidates: list[Candidate],
    *,
    open_client: ClientFactory = _shared_cala,
) -> Visual | None:
    """OpenUI Lang for the reply plus the Cala subgraph it draws, or None when nothing fits."""
    if not candidates:
        return None
    trusted = {r.entity_id for r in profile.reference_investors}
    try:
        text, graph = await walk(
            llm,
            system=system_prompt(profile, candidates),
            question=question,
            open_client=open_client,
            trusted=trusted,
        )
    except LLMError as exc:
        log.info("no visual answer: %s", exc)
        return None
    ui = re.sub(r"^```\w*\n|\n```$", "", (text or "").strip())
    # The chat shows the visual instead of the text, so it must carry its own sentence.
    if not (ui.startswith("root = Answer(") and "Text(" in ui):
        log.debug("no visual answer: %r", ui[:300])
        return None
    if graph is None and any(c in ui for c in EXPLORED_COMPONENTS):
        log.info("no visual answer: it draws a walk that did not happen")
        return None
    names = _known_names(profile, candidates, graph)
    if any(_has_digit(t, names) for t in _TEXT.findall(ui)):
        log.info("no visual answer: a number written in Text")
        return None
    return Visual(ui=ui, graph=graph)


def _known_names(
    profile: Profile, candidates: list[Candidate], graph: ExploredGraph | None
) -> list[str]:
    names = [r.name for r in profile.reference_investors]
    for c in candidates:
        names += [c.name, *(i.name for r in c.rounds for i in r.investors)]
    names += [n.name for n in graph.nodes] if graph else []
    # Longest first, so "500 Global (500 Emerging Europe)" goes before "500 Global".
    return sorted({n for n in names if n}, key=len, reverse=True)


def _has_digit(text: str, names: list[str]) -> bool:
    """Digits outside entity names: values must come from components, never the model."""
    for name in names:
        text = text.replace(name, "")
    return bool(re.search(r"\d", text))

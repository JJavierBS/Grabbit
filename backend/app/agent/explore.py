"""The chat agent walks Cala's entity graph itself, on a fixed budget (#73).

Gemini gets two tools over the Cala client: search by name, and the neighbours of an
entity (introspect, then retrieve only the edges and properties introspection lists).
Every node and edge reached is kept, key properties as sourced `Fact`s, so the chat can
draw what was walked and show each value with its trust badge. Tool results go back to the
model as text: `Message` carries no function parts (app/llm/types.py).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager, AsyncExitStack
from typing import Any

from app.agent.trace import Tracer
from app.cala.client import CalaCacheMiss, CalaClient, CalaError
from app.cala.normalize import edge_attr, edge_fact, property_fact
from app.llm import LLM, Message, ToolCall, ToolResult, ToolSpec
from app.models import ExploredGraph, Fact, GraphEdge, GraphNode

log = logging.getLogger(__name__)

MAX_ROUNDS = 6
MAX_NODES = 30
MAX_NEW_PER_ENTITY = 8
MAX_CALLS_PER_ROUND = 3
MAX_EXPAND = 6
MAX_RELATIONSHIPS = 3
EDGE_LIMIT = 6
SEARCH_LIMIT = 5
# Cala answers most nodes in under a second, but hub nodes can take minutes (cala.md).
CALA_TIMEOUT_S = 15.0
DEADLINE_S = 55.0

SEARCH_TYPES = ["Company", "Organization", "Person", "FundingRound", "Event", "Industry"]
# Listing their neighbours means thousands of edges and timeouts (cala.md "Rate limits").
HUB_TYPES = {"Industry", "Country", "CountrySubdivision", "Event"}
# Properties worth showing, in order, when introspection lists them.
KEY_PROPERTIES = [
    "funding_stage",
    "founding_date",
    "total_funding",
    "employee_count_range",
    "headquarters_address",
    "operational_status",
    "website",
    "round_label",
    "round_type",
    "instrument",
    "transaction_value",
    "event_date",
    "announcement_date",
]
MAX_FACTS = 6
# Edges an investor question needs first; others are listed back so the model can ask.
PREFERRED_RELATIONSHIPS = [
    "PARTICIPATES_IN_FUNDING_ROUND",
    "FOUNDED",
    "IS_CEO_OF",
    "IS_CTO_OF",
    "IS_BOARD_MEMBER_OF",
    "WORKS_AT",
    "IS_SUBSIDIARY_OF",
]
EDGE_DATES = ["event_date", "valid_since", "valid_until"]
ROUND_TYPES = {"FundingRound", "PrivateCompanyFundingRound"}

TOOLS = [
    ToolSpec(
        name="cala_search",
        description=(
            "Find Cala entities by name (fuzzy). Returns up to five hits with id, type and "
            "description; pick the right one before expanding it."
        ),
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name or brand, 1-100 characters"},
                "entity_types": {
                    "type": "array",
                    "items": {"type": "string", "enum": SEARCH_TYPES},
                    "description": "Optional. Investors can be Organization or Company.",
                },
            },
            "required": ["name"],
        },
    ),
    ToolSpec(
        name="cala_neighbours",
        description=(
            "Expand up to six Cala entities: their key sourced properties and their "
            "neighbours over up to three relationship types (a few edges each). Without "
            "relationships it picks funding rounds, founders and executives first, and "
            "lists the other relationship types Cala has for that entity."
        ),
        parameters={
            "type": "object",
            "properties": {
                "entity_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Cala entity ids from the report or earlier results",
                },
                "relationships": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional Cala relationship names, e.g. FOUNDED",
                },
            },
            "required": ["entity_ids"],
        },
    ),
]
TOOL_NAMES = {t.name for t in TOOLS}

ClientFactory = Callable[[], AbstractAsyncContextManager[CalaClient]]


class Walk:
    """The subgraph reached so far, and the Cala session that grows it."""

    def __init__(
        self, open_client: ClientFactory, trusted: set[str], names: dict[str, str] | None = None
    ):
        self._open_client = open_client
        self._stack = AsyncExitStack()
        self._client: CalaClient | None = None
        self.trusted = trusted
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[tuple[str, str, str], GraphEdge] = {}
        self.seen_types: dict[str, str] = {}
        # Names of ids the model may expand before Cala has named them (report startups).
        self.seen_names: dict[str, str] = dict(names or {})
        self.last_hits: list[dict[str, Any]] = []
        self.unavailable = False
        self.cala_calls = 0

    async def __aenter__(self) -> Walk:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._stack.aclose()

    @property
    def full(self) -> bool:
        return len(self.nodes) >= MAX_NODES

    def graph(self) -> ExploredGraph | None:
        if not self.nodes:
            return None
        return ExploredGraph(nodes=list(self.nodes.values()), edges=list(self.edges.values()))

    async def run(self, call: ToolCall) -> str:
        try:
            if call.name == "cala_search":
                return await self._search(call.args)
            return await self._neighbours(call.args)
        except (CalaCacheMiss, ValueError) as err:
            # Replay mode without this walk cached, or no API key: Cala is not reachable.
            log.info("explore: cala unavailable: %s", err)
            self.unavailable = True
            return "Cala is unavailable right now."
        except CalaError as err:
            if err.status in (400, 404, 422):
                return f"Cala rejected that request ({err.status}); check the id or name."
            log.info("explore: cala failed: %s", err)
            self.unavailable = True
            return "Cala is unavailable right now."

    async def _cala(self, method: str, *args: Any, **kwargs: Any) -> Any:
        if self._client is None:
            self._client = await self._stack.enter_async_context(self._open_client())
        self.cala_calls += 1
        return await asyncio.wait_for(
            getattr(self._client, method)(*args, **kwargs), timeout=CALA_TIMEOUT_S
        )

    async def _search(self, args: dict[str, Any]) -> str:
        name = str(args.get("name") or "").strip()[:100]
        if not name:
            return "cala_search needs a name."
        types = [t for t in args.get("entity_types") or [] if t in SEARCH_TYPES] or None
        self.last_hits = []
        try:
            hits = await self._cala("search", name, types, limit=SEARCH_LIMIT)
        except TimeoutError:
            return f"Cala did not answer in time for {name!r}."
        if not hits:
            return f"No Cala entity matches {name!r}."
        self.last_hits = hits
        lines = [f"Search {name!r}:"]
        for hit in hits:
            self.seen_types[hit["id"]] = hit.get("entity_type") or ""
            self.seen_names[hit["id"]] = hit.get("name") or hit["id"]
            description = (hit.get("description") or "")[:140]
            lines.append(f"- {_label(hit, self.trusted)}: {description}")
        return "\n".join(lines)

    async def _neighbours(self, args: dict[str, Any]) -> str:
        ids = [str(i) for i in args.get("entity_ids") or [] if i][:MAX_EXPAND]
        if not ids:
            return "cala_neighbours needs entity_ids."
        wanted = [str(r).upper() for r in args.get("relationships") or []]
        out = []
        for i, entity_id in enumerate(ids):
            if self.unavailable:
                break
            # Share what is left of the budget, so the last ids still get their neighbours.
            allowance = min(
                MAX_NEW_PER_ENTITY, max(2, (MAX_NODES - len(self.nodes)) // (len(ids) - i))
            )
            out.append(await self._expand(entity_id, wanted, allowance))
        return "\n\n".join(out)

    def _edge_priority(self, raw: dict[str, Any]) -> int:
        if edge_attr(raw, "role") == "ISSUER":
            return 0
        if raw.get("id") in self.trusted:
            return 1
        return 2 if edge_attr(raw, "is_lead") is True else 3

    async def _expand(self, entity_id: str, wanted: list[str], allowance: int) -> str:
        if self.seen_types.get(entity_id) in HUB_TYPES:
            return f"{entity_id}: a hub node with thousands of edges; not expanded."
        try:
            intro = await self._cala("introspect", entity_id)
            listed = intro.get("relationships") or {}
            chosen = _choose(listed, wanted)
            props = [p for p in KEY_PROPERTIES if p in (intro.get("properties") or [])]
            props = props[:MAX_FACTS]
            extra = [
                f"{p}{suffix}"
                for p in props
                for suffix in ("_units", "__precision")
                if f"{p}{suffix}" in (intro.get("properties") or [])
            ]
            body = {
                "properties": ["name", *props, *extra],
                "relationships": _projection(chosen),
            }
            data = await self._cala("retrieve", entity_id, body)
        except TimeoutError:
            return f"{entity_id}: Cala did not answer in time."
        facts = {p: property_fact(data, p) for p in props}
        facts = {p: f for p, f in facts.items() if f.value is not None}
        node = self._add_node(entity_id, data.get("name") or entity_id, data.get("entity_type"))
        if node is None:
            return f"{entity_id}: entity budget reached; not added."
        node.facts.update(facts)

        lines = [f"Expanded {_label(data, self.trusted)}"]
        lines += [f"  {p} = {_fact_text(f)}" for p, f in facts.items()]
        skipped = 0
        new_nodes = 0
        for direction, rel in chosen:
            edges = ((data.get("relationships") or {}).get(direction) or {}).get(rel) or []
            if edges:
                lines.append(f"  {direction} {rel}:")
            for raw in sorted(edges, key=self._edge_priority):
                known = raw.get("id") in self.nodes
                if (known or new_nodes < allowance) and self._add_edge(
                    entity_id, direction, rel, raw
                ):
                    new_nodes += 0 if known else 1
                    lines.append(f"    - {_edge_text(raw, self.trusted)}")
                else:
                    skipped += 1
        reached = [
            self.nodes[e.target if e.source == entity_id else e.source].entity_type
            for e in self.edges.values()
            if entity_id in (e.source, e.target)
        ]
        if data.get("entity_type") not in ROUND_TYPES and set(reached) & ROUND_TYPES:
            lines.append(
                "  Funding rounds do not carry the company's name: expand them to see "
                "the company (role ISSUER) and who led or joined."
            )
        if not chosen:
            lines.append("  (no relationship expanded)")
        if skipped:
            lines.append(f"  {skipped} more neighbours left out: entity budget reached.")
        others = sorted({f"{r} ({d})" for d, rels in listed.items() for r in rels} - _names(chosen))
        if others:
            lines.append(f"  Other relationships Cala lists: {', '.join(others)}")
        return "\n".join(lines)

    def _add_node(self, entity_id: str, name: str, entity_type: str | None) -> GraphNode | None:
        node = self.nodes.get(entity_id)
        if node is None:
            if self.full:
                return None
            node = GraphNode(entity_id=entity_id, name=name, entity_type=entity_type or "Entity")
            self.nodes[entity_id] = node
        if entity_type:
            self.seen_types[entity_id] = entity_type
        self.seen_names.setdefault(entity_id, name)
        return node

    def _add_edge(self, entity_id: str, direction: str, rel: str, raw: dict[str, Any]) -> bool:
        other = raw.get("id")
        if (
            not other
            or self._add_node(other, raw.get("name") or other, raw.get("entity_type")) is None
        ):
            return False
        source, target = (entity_id, other) if direction == "outgoing" else (other, entity_id)
        key = (source, target, rel)
        if key not in self.edges:
            role = edge_attr(raw, "role")
            self.edges[key] = GraphEdge(
                source=source,
                target=target,
                relationship=rel,
                role=str(role) if role else None,
                is_lead=edge_attr(raw, "is_lead") is True,
                facts={d: f for d in EDGE_DATES if (f := edge_fact(raw, d)).value is not None},
            )
        return True


def _choose(listed: dict[str, list[str]], wanted: list[str]) -> list[tuple[str, str]]:
    pairs = [(d, r) for d in ("outgoing", "incoming") for r in listed.get(d) or []]
    if wanted:
        chosen = [p for w in wanted for p in pairs if p[1] == w]
    else:
        chosen = [p for r in PREFERRED_RELATIONSHIPS for p in pairs if p[1] == r]
    return list(dict.fromkeys(chosen))[:MAX_RELATIONSHIPS]


def _projection(chosen: list[tuple[str, str]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for direction, rel in chosen:
        out.setdefault(direction, {})[rel] = {"limit": EDGE_LIMIT}
    return out


def _names(chosen: list[tuple[str, str]]) -> set[str]:
    return {f"{r} ({d})" for d, r in chosen}


def _label(entity: dict[str, Any], trusted: set[str]) -> str:
    mark = ", trusted by the angel" if entity.get("id") in trusted else ""
    return f"{entity.get('name')} [{entity.get('entity_type')}, id {entity.get('id')}{mark}]"


def _edge_text(raw: dict[str, Any], trusted: set[str]) -> str:
    attrs = [
        f"role {role}" if (role := edge_attr(raw, "role")) else "",
        "lead" if edge_attr(raw, "is_lead") is True else "",
        *(f"{d} {_fact_text(f)}" for d in EDGE_DATES if (f := edge_fact(raw, d)).value),
    ]
    detail = ", ".join(a for a in attrs if a)
    return _label(raw, trusted) + (f" ({detail})" if detail else "")


def _fact_text(fact: Fact) -> str:
    value = fact.value if not isinstance(fact.value, list) else ", ".join(map(str, fact.value))
    unit = f" {fact.unit}" if fact.unit else ""
    return f"{value}{unit} ({fact.trust})"


def _describe(call: ToolCall) -> str:
    args = ", ".join(f"{k}={v!r}" for k, v in call.args.items())
    return f"{call.name}({args})"


async def walk(
    llm: LLM,
    *,
    system: str,
    question: str,
    open_client: ClientFactory,
    trusted: set[str],
    check: Callable[[str, ExploredGraph | None], str | None] | None = None,
    clock: Callable[[], float] = time.monotonic,
    tracer: Tracer | None = None,
    names: dict[str, str] | None = None,
) -> tuple[str, ExploredGraph | None]:
    """Let the model call Cala tools for a few rounds, then return its answer and the walk.

    `check` names a problem in the answer (e.g. a number in Text); the model gets one rewrite.
    `tracer` shows each step, the growing subgraph and the streamed answer in the chat.
    """
    started = clock()
    messages = [Message(role="user", text=question)]
    on_text = tracer.answer if tracer else None
    async with Walk(open_client, trusted, names) as state:
        rounds = 0
        tools: list[ToolSpec] | None = TOOLS
        while True:
            result = await llm.chat(system=system, messages=messages, tools=tools, on_text=on_text)
            if tracer and result.thoughts:
                tracer.thought(result.thoughts)
            calls = result.tool_calls
            if tools is None or not any(c.name in TOOL_NAMES for c in calls):
                break
            rounds += 1
            round_started = clock()
            if tracer:
                tracer.drop_answer()
                tracer.round(rounds)
            # Gemini expects one response per call it made, even the ones we skip.
            outputs = []
            for i, call in enumerate(calls):
                if call.name not in TOOL_NAMES:
                    outputs.append(f"Unknown tool {call.name}.")
                elif i >= MAX_CALLS_PER_ROUND:
                    outputs.append(f"Skipped: at most {MAX_CALLS_PER_ROUND} calls per round.")
                elif tracer:
                    outputs.append(await _traced(state, call, tracer))
                else:
                    outputs.append(await state.run(call))
            log.info(
                "explore round %d: %s (%.1fs)",
                rounds,
                "; ".join(map(_describe, calls)),
                clock() - round_started,
            )
            log.debug("explore results:\n%s", "\n\n".join(outputs))
            stop = _stop_reason(state, rounds, clock() - started)
            if stop:
                tools = None
            note = stop or (
                f"Round {rounds} of {MAX_ROUNDS}, {len(state.nodes)} of {MAX_NODES} entities. "
                "Call more Cala tools, or answer in OpenUI Lang."
            )
            messages += [
                Message(role="model", text=result.text, tool_calls=calls),
                Message(
                    role="user",
                    text=note,
                    tool_results=[
                        ToolResult(name=c.name, id=c.id, output=o)
                        for c, o in zip(calls, outputs, strict=True)
                    ],
                ),
            ]
        graph = state.graph()
        problem = check(result.text, graph) if check else None
        if problem:
            # One rewrite, without tools: cheaper than losing the whole visual answer.
            log.info("explore: asking for a rewrite: %s", problem)
            messages += [
                Message(role="model", text=result.text),
                Message(role="user", text=f"{problem} Rewrite the answer in OpenUI Lang."),
            ]
            if tracer:
                # The streamed draft broke a rule; say so instead of swapping it silently.
                tracer.drop_answer()
                tracer.note("rewrite", "Rewriting the answer so every number comes from Cala")
            result = await llm.chat(system=system, messages=messages, on_text=on_text)
        log.info(
            "explore: %d tool rounds, %d cala calls, %d nodes, %d edges, %.1fs",
            rounds,
            state.cala_calls,
            len(state.nodes),
            len(state.edges),
            clock() - started,
        )
        return result.text, graph


async def _traced(state: Walk, call: ToolCall, tracer: Tracer) -> str:
    before = set(state.nodes)
    kind = "search" if call.name == "cala_search" else "expand"
    step = tracer.start(kind, _step_text(call, state))
    output = await state.run(call)
    if call.name == "cala_neighbours":
        ids = [str(i) for i in call.args.get("entity_ids") or [] if i]
        root = next((i for i in ids if i in state.nodes), None)
        tracer.graph(state.graph(), root)
    await tracer.finish(step, _step_result(call, state, before, output))
    return output


# Plain words for the live walk (#138): what a person would call each thing, no graph jargon.
FOUND_ORDER = ["startup", "investor", "founder", "person", "funding round", "company"]
PLURALS = {"person": "people", "company": "companies"}
SEARCH_KINDS = {"Person": "person", "Event": "event", "Industry": "sector"}


def _step_text(call: ToolCall, state: Walk) -> str:
    if call.name == "cala_search":
        name = str(call.args.get("name") or "").strip()[:100]
        return f"Searching Cala for “{name}”"
    ids = [str(i) for i in call.args.get("entity_ids") or [] if i][:MAX_EXPAND]
    rounds = [i for i in ids if state.seen_types.get(i) in ROUND_TYPES]
    others = [i for i in ids if i not in rounds]
    if not others:
        if len(rounds) == 1:
            return "Opening a funding round to see who raised and who invested"
        return f"Opening {len(rounds)} funding rounds to see who raised and who invested"
    names = [state.seen_names.get(i) or "a company from your report" for i in others]
    if len(others) == 1 and not rounds:
        if state.seen_types.get(others[0]) == "Person":
            return f"Looking at what {names[0]} founded and where they work"
        return f"Looking at {_possessive(names[0])} funding rounds and people"
    parts = names[:2] + ([f"{len(names) - 2} more"] if len(names) > 2 else [])
    if rounds:
        parts.append(_count(len(rounds), "funding round"))
    return f"Looking at {_join(parts)}"


def _step_result(call: ToolCall, state: Walk, before: set[str], output: str) -> str:
    if state.unavailable:
        return "Cala is not reachable right now"
    if "did not answer in time" in output:
        return "Cala took too long, moving on"
    if call.name == "cala_search":
        hits = state.last_hits
        if not hits:
            return "nothing by that name"
        kind = SEARCH_KINDS.get(hits[0].get("entity_type") or "")
        return f"found {hits[0].get('name')}" + (f" ({kind})" if kind else "")
    # What the step reached, not the entities it opened (those were found earlier).
    opened = {str(i) for i in call.args.get("entity_ids") or []}
    new = [state.nodes[i] for i in state.nodes if i not in before and i not in opened]
    if not new:
        if "hub node" in output:
            return "too big to open: thousands of connections"
        return "nothing new"
    counts: dict[str, int] = {}
    for node in new:
        what = _what(node.entity_id, node.entity_type, state)
        counts[what] = counts.get(what, 0) + 1
    found = [_count(counts[w], w) for w in FOUND_ORDER if w in counts]
    # Cala names funds by their vehicle: "500 Global (500 Emerging Europe)" reads "500 Global".
    trusted = [n.name.split(" (")[0] for n in new if n.entity_id in state.trusted]
    note = f", including {_join(trusted[:2])}, whom you trust" if trusted else ""
    return f"found {_join(found)}{note}"


def _what(entity_id: str, entity_type: str, state: Walk) -> str:
    """What a person would call an entity, from its type and how the walk reached it."""
    if entity_type in ROUND_TYPES:
        return "funding round"
    edges = [e for e in state.edges.values() if entity_id in (e.source, e.target)]
    if entity_type == "Person":
        return "founder" if any(e.relationship == "FOUNDED" for e in edges) else "person"
    roles = {e.role for e in edges}
    if "ISSUER" in roles:
        return "startup"
    if "INVESTOR" in roles or any(e.relationship == "PARTICIPATES_IN_FUNDING_ROUND" for e in edges):
        return "investor"
    return "company"


def _possessive(name: str) -> str:
    return f"{name}’" if name.endswith("s") else f"{name}’s"


def _count(n: int, what: str) -> str:
    return f"{n} {what if n == 1 else PLURALS.get(what, what + 's')}"


def _join(parts: list[str]) -> str:
    return parts[0] if len(parts) == 1 else f"{', '.join(parts[:-1])} and {parts[-1]}"


def _stop_reason(state: Walk, rounds: int, elapsed: float) -> str | None:
    answer = " Answer now in OpenUI Lang, without tools."
    if state.unavailable:
        return (
            "Cala is unavailable right now: answer from the report only, without "
            f"ExploredGraph or EntityFacts, or output exactly NONE.{answer}"
        )
    if rounds >= MAX_ROUNDS or state.full or elapsed > DEADLINE_S:
        return f"The exploration budget is used up.{answer}"
    return None

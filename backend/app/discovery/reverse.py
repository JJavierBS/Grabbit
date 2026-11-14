"""Reverse walk: trusted investors -> their funding rounds -> issuers attending the event.

The event walk reads the first attendees only, so most startups a trusted fund backed are
never opened (#191). This walk starts from the fund instead: every Cala entity of the fund
(one fund is many entities, cala.md "Data quirks"), each entity's outgoing
`PARTICIPATES_IN_FUNDING_ROUND` edges, each round's `ISSUER`, crossed by entity id with the
event's attendee list. Attending issuers become candidates through the event walk's own path.
The investor -> round edge carries no date, so rounds are read in the order Cala lists them.

A second ring (#193) then walks, the same way, the investors that most often funded those
rounds next to a trusted one, so the walk also reaches the startups of a trusted fund's
usual co-investors.
"""

from __future__ import annotations

import asyncio
import copy
import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.cala.client import CalaCacheMiss, CalaError
from app.cala.normalize import edge_attr, relationships
from app.discovery.build import (
    build_candidate,
    build_round,
    headcount_series,
    issuer_id,
    issuer_round_ids,
    normalise_name,
)
from app.discovery.filters import is_startup
from app.discovery.links import (
    FUNDING_ROLES,
    PARTICIPATES,
    InvestorRounds,
    LinkGraph,
    Trusted,
    _funders,
)
from app.discovery.pipeline import (
    INVESTOR_BODY,
    ROUND_BODY,
    SLUSH_2026,
    Limits,
    attendees,
    fetch_company,
    lead_portfolios,
)
from app.models import Candidate, ReferenceInvestor
from app.references import UNRESOLVED
from app.signals.core import SignalInputs, compute_signals

log = logging.getLogger(__name__)

EDGE_PAGE = INVESTOR_BODY["relationships"]["outgoing"][PARTICIPATES]["limit"]


@dataclass
class ReverseLimits:
    search_limit: int = 50
    timeout: float = 25.0  # hub funds can take minutes (cala.md "Rate limits and latency")
    call_budget: int | None = 300  # new Cala calls per walk; cached reads are free
    # Attendee paging, rounds per company and lead rounds: the event walk's own, so both
    # walks ask Cala the same questions and share the cache.
    event: Limits = field(default_factory=Limits)
    second_ring: bool = True
    co_investors: int = 10  # walked per trusted investor, most shared rounds first
    min_shared_rounds: int = 2
    # A co-investor with more round edges than this is a hub: reading its rounds would eat
    # the budget (cala.md "Rate limits and latency"). `None` walks every co-investor.
    hub_round_edges: int | None = 300


@dataclass
class ReverseStats:
    """`entities` counts the trusted funds' entities; `rounds`, `issuers`, `attending` and
    `startups` count both rings."""

    entities: int = 0
    rounds: int = 0
    issuers: int = 0
    attending: int = 0
    startups: int = 0
    skipped: int = 0
    budget_spent: bool = False
    co_investors: int = 0  # distinct names seen next to a trusted investor
    co_investors_walked: int = 0
    co_investors_skipped: int = 0  # hubs
    second_ring_startups: int = 0


@dataclass
class CoInvestor:
    name: str
    entity_ids: list[str]
    shared_rounds: int
    trusted: str  # the reference investor it shares those rounds with


@dataclass
class ReverseResult:
    candidates: list[Candidate] = field(default_factory=list)
    # The fund entities with the rounds read for each, and those rounds raw, plus the
    # candidates' own rounds: merge into the event walk's graph with `merge_graphs`.
    links: LinkGraph = field(default_factory=LinkGraph)
    # Normalised name -> entity id of the fund entities and of the candidates' investors.
    investors: dict[str, str] = field(default_factory=dict)
    raw: dict[str, dict[str, Any]] = field(default_factory=dict)
    # The co-investors chosen for the second ring, strongest first, hubs included.
    co_investors: list[CoInvestor] = field(default_factory=list)
    stats: ReverseStats = field(default_factory=ReverseStats)


class BudgetSpent(CalaError):
    def __init__(self) -> None:
        super().__init__(429, "reverse walk call budget spent")


class _Bounded:
    """Cala behind the walk's budget of new calls and its per-call timeout."""

    def __init__(self, client: Any, limits: ReverseLimits):
        self.client = client
        self.limits = limits
        self.start = getattr(client, "calls_made", 0)

    @property
    def spent(self) -> bool:
        budget = self.limits.call_budget
        return budget is not None and getattr(self.client, "calls_made", 0) - self.start >= budget

    async def _run[R](self, call: Callable[[], Awaitable[R]]) -> R:
        if self.spent:
            raise BudgetSpent()
        try:
            return await asyncio.wait_for(call(), self.limits.timeout)
        except TimeoutError:
            raise CalaError(504, f"no answer in {self.limits.timeout:g} s") from None

    async def search(self, name: str, limit: int) -> list[dict[str, Any]]:
        return await self._run(lambda: self.client.search(name, limit=limit))

    async def introspect(self, entity_id: str) -> dict[str, Any]:
        return await self._run(lambda: self.client.introspect(entity_id))

    async def retrieve(
        self, entity_id: str, body: dict[str, Any] | None = None, *, fresh: bool = False
    ) -> dict:
        return await self._run(lambda: self.client.retrieve(entity_id, body, fresh=fresh))


async def reverse_walk(
    client: Any,
    references: list[ReferenceInvestor],
    event_id: str | None = None,
    today: date | None = None,
    limits: ReverseLimits | None = None,
) -> ReverseResult:
    """Startups attending the event that the reference investors funded, unfiltered.

    Never raises on a Cala error, a cache miss, a timeout or a spent budget: it returns what
    it has built so far (`stats.budget_spent`, `stats.skipped`).
    """
    result = ReverseResult()
    if not references:
        return result
    today = today or date.today()
    limits = limits or ReverseLimits()
    cala = _Bounded(client, limits)
    stats = result.stats

    try:
        stubs = await attendees(cala, event_id or SLUSH_2026, limits.event)
    except (CalaError, CalaCacheMiss) as err:
        log.warning("reverse walk: no attendee list, nothing to cross: %s", err)
        stats.budget_spent = cala.spent
        return result
    attending = {s["id"]: s for s in stubs if s.get("entity_type") in (None, "Company")}

    walk = _Walk(cala, today, limits, result, attending)
    first_ring: list[tuple[ReferenceInvestor, list[InvestorRounds]]] = []
    for ref in references:
        funds: list[InvestorRounds] = []
        first_ring.append((ref, funds))
        for entity_id in await _fund_entities(cala, ref, limits):
            if entity_id in result.links.investors or cala.spent:
                continue
            fund, _ = await _fund_rounds(cala, entity_id, ref.name)
            if fund is None:
                stats.skipped += 1
                continue
            stats.entities += 1
            funds.append(fund)
            await walk.rounds_of(fund)
    if limits.second_ring:
        reached = len(result.candidates)
        await _second_ring(walk, first_ring, Trusted(references))
        stats.second_ring_startups = len(result.candidates) - reached
    stats.startups = len(result.candidates)
    stats.budget_spent = cala.spent
    if stats.budget_spent:
        log.warning("reverse walk: call budget spent, returning what was read")
    result.investors.update(
        {
            normalise_name(i.name): i.entity_id
            for c in result.candidates
            for r in c.rounds
            for i in r.investors
        }
    )
    return result


@dataclass
class _Walk:
    cala: _Bounded
    today: date
    limits: ReverseLimits
    result: ReverseResult
    attending: dict[str, dict[str, Any]]
    seen_issuers: set[str] = field(default_factory=set)
    seen_names: set[str] = field(default_factory=set)

    async def rounds_of(self, fund: InvestorRounds) -> None:
        """Read the investor's rounds; their issuers attending the event become candidates."""
        cala, result = self.cala, self.result
        stats, links = result.stats, result.links
        links.investors[fund.entity_id] = fund
        result.investors.setdefault(normalise_name(fund.name), fund.entity_id)
        read: list[str] = []
        for rid in fund.round_ids:
            node = links.rounds.get(rid)
            if node is None:
                if cala.spent:
                    break
                node = await _read(cala, rid, ROUND_BODY)
                if node is None:
                    continue
                result.raw[rid] = links.rounds[rid] = node
                stats.rounds += 1
            read.append(rid)
            issuer = issuer_id(node)
            if issuer is None or issuer in self.seen_issuers:
                continue
            self.seen_issuers.add(issuer)
            stats.issuers += 1
            stub = self.attending.get(issuer)
            if stub is None:
                continue
            stats.attending += 1
            key = normalise_name(stub.get("name")) or issuer
            if key in self.seen_names:
                continue  # brand and legal entity both attending
            self.seen_names.add(key)
            candidate = await _candidate(cala, issuer, self.today, self.limits, result)
            if candidate is not None:
                result.candidates.append(candidate)
        fund.round_ids = read


async def _second_ring(
    walk: _Walk,
    first_ring: list[tuple[ReferenceInvestor, list[InvestorRounds]]],
    trusted: Trusted,
) -> None:
    cala, limits, result = walk.cala, walk.limits, walk.result
    stats, links = result.stats, result.links
    result.co_investors, stats.co_investors = _strongest_co_investors(
        first_ring, links, trusted, limits
    )
    cap = limits.hub_round_edges
    for co in result.co_investors:
        if cala.spent:
            break
        funds: list[InvestorRounds] = []
        edges = 0
        for entity_id in co.entity_ids:
            if entity_id in links.investors:
                continue
            left = None if cap is None else cap - edges
            fund, read = await _fund_rounds(cala, entity_id, co.name, left)
            edges += read
            if cap is not None and edges > cap:
                break
            if fund is not None:
                funds.append(fund)
        if cap is not None and edges > cap:
            stats.co_investors_skipped += 1
            log.warning(
                "reverse walk: skipping hub co-investor %s, more than %d round edges",
                co.name,
                cap,
            )
            continue
        if not funds:
            continue
        stats.co_investors_walked += 1
        for fund in funds:
            await walk.rounds_of(fund)


def _strongest_co_investors(
    first_ring: list[tuple[ReferenceInvestor, list[InvestorRounds]]],
    graph: LinkGraph,
    trusted: Trusted,
    limits: ReverseLimits,
) -> tuple[list[CoInvestor], int]:
    """(Co-investors to walk, strongest first; distinct co-investor names seen).

    A co-investor funded a round next to a trusted investor. Cala gives it one entity id per
    round and one fund is several entities, so rounds are counted per normalised name.
    """
    seen: set[str] = set()
    chosen: dict[str, CoInvestor] = {}
    for ref, funds in first_ring:
        shared: dict[str, set[str]] = {}
        found: dict[str, CoInvestor] = {}
        for rid in dict.fromkeys(rid for fund in funds for rid in fund.round_ids):
            for edge in _funders(graph.rounds[rid]):
                if edge["id"] in graph.investors or trusted.match(edge["id"], edge.get("name")):
                    continue
                key = normalise_name(edge.get("name")) or edge["id"]
                co = found.setdefault(
                    key, CoInvestor(edge.get("name") or edge["id"], [], 0, ref.name)
                )
                if edge["id"] not in co.entity_ids:
                    co.entity_ids.append(edge["id"])
                shared.setdefault(key, set()).add(rid)
        seen.update(found)
        for key, co in found.items():
            co.shared_rounds = len(shared[key])
        ranked = sorted(found, key=lambda key: (-found[key].shared_rounds, key))
        strong = [k for k in ranked if found[k].shared_rounds >= limits.min_shared_rounds]
        for key in strong[: max(limits.co_investors, 0)]:
            co, other = found[key], chosen.get(key)
            if other is None:
                chosen[key] = co
                continue
            best = max(other, co, key=lambda c: c.shared_rounds)
            more = [i for i in co.entity_ids if i not in other.entity_ids]
            chosen[key] = CoInvestor(
                best.name, other.entity_ids + more, best.shared_rounds, best.trusted
            )
    order = sorted(chosen, key=lambda key: (-chosen[key].shared_rounds, key))
    return [chosen[key] for key in order], len(seen)


async def _fund_entities(
    cala: _Bounded, ref: ReferenceInvestor, limits: ReverseLimits
) -> list[str]:
    """Every Cala entity of the fund: its stored id, then name-search hits under the fund's
    name or the name followed by more words ("Y Combinator W24")."""
    ids = [] if ref.entity_id.startswith(UNRESOLVED) else [ref.entity_id]
    if cala.spent:
        return ids
    try:
        hits = await cala.search(ref.name, limits.search_limit)
    except (CalaError, CalaCacheMiss) as err:
        log.warning("reverse walk: cannot search %r: %s", ref.name, err)
        return ids
    by_name = Trusted([ReferenceInvestor(entity_id=f"{UNRESOLVED}{ref.name}", name=ref.name)])
    for hit in hits:
        if hit["id"] not in ids and by_name.match(hit["id"], hit.get("name")):
            ids.append(hit["id"])
    return ids


async def _fund_rounds(
    cala: _Bounded, entity_id: str, fallback_name: str, edge_cap: int | None = None
) -> tuple[InvestorRounds | None, int]:
    """(The rounds this entity funded, the round edges read to list them).

    Reads every page, or stops at the page that takes the edges past `edge_cap`. The rounds
    are `None` when the first page cannot be read.
    """
    # The first page is the investor read of the event walk, so both share one cache entry.
    first = await _read(cala, entity_id, INVESTOR_BODY)
    if first is None:
        return None, 0
    round_ids: list[str] = []
    page, offset, edges_read = first, 0, 0
    while True:
        edges = relationships(page, "outgoing", PARTICIPATES)
        edges_read += len(edges)
        for edge in edges:
            funded = str(edge_attr(edge, "role") or "").upper() in FUNDING_ROLES
            if funded and edge["id"] not in round_ids:
                round_ids.append(edge["id"])
        if len(edges) < EDGE_PAGE or (edge_cap is not None and edges_read > edge_cap):
            break
        offset += EDGE_PAGE
        body = copy.deepcopy(INVESTOR_BODY)
        body["relationships"]["outgoing"][PARTICIPATES]["offset"] = offset
        page = await _read(cala, entity_id, body)
        if page is None:
            break
    fund = InvestorRounds(
        entity_id=entity_id,
        name=first.get("name") or fallback_name,
        entity_type=first.get("entity_type") or "Organization",
        round_ids=round_ids,
    )
    return fund, edges_read


async def _candidate(
    cala: _Bounded, company_id: str, today: date, limits: ReverseLimits, result: ReverseResult
) -> Candidate | None:
    """The event walk's path for one attendee: company, startup rules, rounds, signals."""
    raw = result.raw
    try:
        company = await fetch_company(cala, company_id)
        raw[company["id"]] = company
        if not is_startup(company, today, limits.event.rules):
            return None
        rounds = []
        for rid in issuer_round_ids(company)[: limits.event.max_rounds_per_company]:
            node = raw.get(rid) or await cala.retrieve(rid, ROUND_BODY)
            raw[rid] = result.links.rounds[rid] = node
            rounds.append(build_round(node))
        candidate = build_candidate(company, rounds)
        inputs = SignalInputs(
            reference_investors=[],
            headcount_series=headcount_series(company),
            lead_portfolios=await lead_portfolios(cala, candidate, limits.event, raw),
        )
        return candidate.model_copy(update={"signals": compute_signals(candidate, inputs, today)})
    except (CalaError, CalaCacheMiss) as err:
        result.stats.skipped += 1
        log.warning("reverse walk: skipping issuer %s: %s", company_id, err)
        return None


async def _read(cala: _Bounded, entity_id: str, body: dict[str, Any]) -> dict[str, Any] | None:
    try:
        return await cala.retrieve(entity_id, body)
    except (CalaCacheMiss, BudgetSpent):
        log.debug("reverse walk: %s not read", entity_id)  # expected in replay before warm
        return None
    except CalaError as err:
        log.warning("reverse walk: skipping %s: %s", entity_id, err)
        return None


def merge_candidates(event: list[Candidate], reverse: list[Candidate]) -> list[Candidate]:
    """The event walk's candidates, then the reverse walk's that are not among them by
    entity id or normalised name."""
    merged = list(event)
    ids = {c.entity_id for c in merged}
    names = {normalise_name(c.name) for c in merged} - {""}
    for candidate in reverse:
        name = normalise_name(candidate.name)
        if candidate.entity_id in ids or name in names:
            continue
        ids.add(candidate.entity_id)
        if name:
            names.add(name)
        merged.append(candidate)
    return merged


def merge_graphs(base: LinkGraph, extra: LinkGraph) -> LinkGraph:
    """A new graph with both walks' investors and rounds; neither input is changed."""
    investors = dict(base.investors)
    for entity_id, theirs in extra.investors.items():
        ours = investors.get(entity_id)
        if ours is None:
            investors[entity_id] = theirs
            continue
        more = [rid for rid in theirs.round_ids if rid not in ours.round_ids]
        investors[entity_id] = InvestorRounds(
            entity_id=entity_id,
            name=ours.name,
            entity_type=ours.entity_type,
            round_ids=ours.round_ids + more,
        )
    return LinkGraph(investors=investors, rounds={**extra.rounds, **base.rounds})

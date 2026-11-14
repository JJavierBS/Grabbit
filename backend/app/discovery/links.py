"""Hidden links: second-degree relationships in Cala's graph that one company page does not show.

Two kinds, both proved by `FundingRound` participants and their `role` (cala.md: the
`INVESTED_IN` edge is noisy in direction, so it is never used):
- `trusted_co_investor`: an investor in the startup's rounds has invested in other rounds
  alongside an investor the angel trusts.
- `shared_investor`: an investor in the startup's rounds also backs another startup on the list.

The walk (`walk_investors`) does not depend on the profile, so `make warm` fills the cache for
any set of trusted investors; matching (`hidden_links`) is pure and runs again whenever the
reference investors change. Founder background was probed and dropped: on the Slush sample
the founders' `Person` nodes link only to their current company (decisions.md).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import Any

from app.cala.client import CalaCacheMiss, CalaError
from app.cala.normalize import STRENGTH, UNRANKED, edge_attr, relationships, strongest, to_source
from app.discovery.build import normalise_name
from app.models import (
    Candidate,
    Fact,
    HiddenLink,
    Investor,
    LinkEdge,
    LinkNode,
    ReferenceInvestor,
    Round,
    Source,
    TrustLevel,
)

log = logging.getLogger(__name__)

PARTICIPATES = "PARTICIPATES_IN_FUNDING_ROUND"
# GRANTOR is not in the field guide; FIRSTPICK shows it on a round next to INVESTORs.
FUNDING_ROLES = ("INVESTOR", "LENDER", "GRANTOR")
MAX_LINKS_PER_KIND = 3
MAX_PROOF_ROUNDS = 3


@dataclass
class InvestorRounds:
    entity_id: str
    name: str
    entity_type: str
    round_ids: list[str]


@dataclass
class LinkGraph:
    """What the walk read: each investor's rounds and every round node seen, raw."""

    investors: dict[str, InvestorRounds] = field(default_factory=dict)
    rounds: dict[str, dict[str, Any]] = field(default_factory=dict)


@dataclass
class LinkLimits:
    investors_per_startup: int = 5
    rounds_per_investor: int = 15
    timeout: float = 25.0  # hub funds can take minutes (cala.md "Rate limits and latency")
    call_budget: int | None = 300  # new Cala calls per walk; cached reads are free


def newest_first(rounds: list[Round]) -> list[Round]:
    return sorted(rounds, key=lambda r: str(r.date.value or ""), reverse=True)


def walk_order(candidate: Candidate) -> list[Investor]:
    """Investors of the startup, newest round first and leads first, one per fund name."""
    rounds = newest_first(candidate.rounds)
    seen: set[str] = set()
    ordered: list[Investor] = []
    for round_ in rounds:
        for inv in sorted(round_.investors, key=lambda i: not i.is_lead):
            key = normalise_name(inv.name) or inv.entity_id
            if key not in seen:
                seen.add(key)
                ordered.append(inv)
    return ordered


async def walk_investors(
    client: Any,
    candidates: list[Candidate],
    raw: dict[str, dict[str, Any]],
    limits: LinkLimits,
    investor_body: dict[str, Any],
    round_body: dict[str, Any],
) -> LinkGraph:
    """Read each startup's first investors and their latest rounds, serially and within budget."""
    graph = LinkGraph(
        rounds={
            r.entity_id: raw[r.entity_id]
            for c in candidates
            for r in c.rounds
            if r.entity_id in raw
        }
    )
    start = getattr(client, "calls_made", 0)

    def over_budget() -> bool:
        spent = getattr(client, "calls_made", 0) - start
        return limits.call_budget is not None and spent >= limits.call_budget

    async def read(entity_id: str, body: dict[str, Any]) -> dict[str, Any] | None:
        return await _bounded(client.retrieve(entity_id, body), limits.timeout, entity_id)

    for candidate in candidates:
        for inv in walk_order(candidate)[: limits.investors_per_startup]:
            if inv.entity_id in graph.investors:
                continue
            if over_budget():
                log.warning("hidden links: call budget spent, stopping the walk")
                return graph
            node = raw.get(inv.entity_id) or await read(inv.entity_id, investor_body)
            if node is None:
                continue
            raw[inv.entity_id] = node
            round_ids = [
                e["id"]
                for e in relationships(node, "outgoing", PARTICIPATES)
                if str(edge_attr(e, "role") or "").upper() in FUNDING_ROLES
            ][: limits.rounds_per_investor]
            for rid in round_ids:
                if rid in graph.rounds:
                    continue
                if over_budget():
                    break
                round_node = raw.get(rid) or await read(rid, round_body)
                if round_node is not None:
                    raw[rid] = graph.rounds[rid] = round_node
            graph.investors[inv.entity_id] = InvestorRounds(
                entity_id=inv.entity_id,
                name=node.get("name") or inv.name,
                entity_type=node.get("entity_type") or "Organization",
                round_ids=[rid for rid in round_ids if rid in graph.rounds],
            )
    return graph


async def _bounded[R](call: Awaitable[R], seconds: float, entity_id: str) -> R | None:
    try:
        return await asyncio.wait_for(call, seconds)
    except CalaCacheMiss:
        log.debug("hidden links: %s not warmed", entity_id)  # expected in replay before warm
        return None
    except (TimeoutError, CalaError) as err:
        log.warning("hidden links: skipping %s: %s", entity_id, err or "timeout")
        return None


class Trusted:
    """Reference investors matched by Cala id or by name: one fund is often several entities."""

    def __init__(self, reference: list[ReferenceInvestor]):
        self.by_id = {r.entity_id: r for r in reference}
        self.by_name = {normalise_name(r.name): r for r in reference if normalise_name(r.name)}

    def match(self, entity_id: str, name: str | None) -> ReferenceInvestor | None:
        if entity_id in self.by_id:
            return self.by_id[entity_id]
        key = normalise_name(name)
        if not key:
            return None
        if key in self.by_name:
            return self.by_name[key]
        # "500 Global" vs "500 Global (500 Emerging Europe)": same rule as app/references.py,
        # two words at least so one common word never matches.
        for ref_key, ref in self.by_name.items():
            short, long_ = sorted((key, ref_key), key=len)
            if len(short.split()) >= 2 and long_.startswith(f"{short} "):
                return ref
        return None


def hidden_links(
    candidate: Candidate,
    graph: LinkGraph,
    reference: list[ReferenceInvestor],
    shortlist: list[Candidate],
) -> list[HiddenLink]:
    trusted = Trusted(reference)
    return (
        trusted_co_investors(candidate, graph, trusted)[:MAX_LINKS_PER_KIND]
        + shared_investors(candidate, graph, trusted, shortlist)[:MAX_LINKS_PER_KIND]
    )


def attach_links(
    candidates: list[Candidate], graph: LinkGraph, reference: list[ReferenceInvestor]
) -> list[Candidate]:
    return [
        c.model_copy(update={"links": hidden_links(c, graph, reference, candidates)})
        for c in candidates
    ]


@dataclass
class _Proof:
    round_id: str
    via_edge: dict[str, Any]
    other_edge: dict[str, Any]


def trusted_co_investors(
    candidate: Candidate, graph: LinkGraph, trusted: Trusted
) -> list[HiddenLink]:
    """Rounds anywhere in the walk where one of its investors sat next to a trusted one."""
    own = {r.entity_id for r in candidate.rounds}
    links: list[tuple[tuple[int, bool], HiddenLink]] = []
    for inv in walk_order(candidate):
        if trusted.match(inv.entity_id, inv.name):
            continue
        key = normalise_name(inv.name)
        by_ref: dict[str, tuple[ReferenceInvestor, list[_Proof]]] = {}
        for rid, node in graph.rounds.items():
            if rid in own:
                continue  # a trusted investor in its own rounds is the co-invest signal
            funders = _funders(node)
            via = next((e for e in funders if _same(e, inv.entity_id, key)), None)
            if via is None:
                continue
            for edge in funders:
                ref = (
                    None
                    if _same(edge, inv.entity_id, key)
                    else trusted.match(edge["id"], edge.get("name"))
                )
                if ref:
                    proofs = by_ref.setdefault(ref.entity_id, (ref, []))[1]
                    if all(p.round_id != rid for p in proofs):
                        proofs.append(_Proof(rid, via, edge))
        for ref, proofs in by_ref.values():
            link = _co_investor_link(candidate, inv, ref, proofs, graph)
            links.append(((len(proofs), inv.is_lead), link))
    links.sort(key=lambda pair: pair[0], reverse=True)
    return [link for _, link in links]


def _co_investor_link(
    candidate: Candidate,
    inv: Investor,
    ref: ReferenceInvestor,
    proofs: list[_Proof],
    graph: LinkGraph,
) -> HiddenLink:
    start = _startup_branch(candidate, inv, graph)
    nodes, edges, trusts = start.nodes, start.edges, start.trusts
    facts: list[Fact] = []
    target: LinkNode | None = None
    issuers: list[str] = []
    for proof in proofs[:MAX_PROOF_ROUNDS]:
        node = graph.rounds[proof.round_id]
        issuer = _issuer(node)
        issuer_name = issuer.get("name") if issuer else None
        issuers.append(issuer_name or "an unnamed company")
        round_node = LinkNode(
            entity_id=proof.round_id, name=_round_name(node), entity_type="FundingRound"
        )
        other = LinkNode(
            entity_id=proof.other_edge["id"],
            name=proof.other_edge.get("name") or ref.name,
            entity_type=proof.other_edge.get("entity_type") or "Organization",
        )
        target = target or other
        if proof.via_edge["id"] != inv.entity_id:  # same fund, another Cala entity
            _add(nodes, _node(proof.via_edge, "Organization"))
        _add(nodes, round_node, other)
        edges += [
            _edge(proof.via_edge["id"], proof.round_id, proof.via_edge),
            _edge(other.entity_id, proof.round_id, proof.other_edge),
        ]
        trusts += [_edge_trust(proof.via_edge), _edge_trust(proof.other_edge)]
        if issuer:
            _add(nodes, _node(issuer, "Company"))
            edges.append(_edge(issuer["id"], proof.round_id, issuer))
        facts.append(_proof_fact(f"{issuer_name or 'Unnamed company'} · {round_node.name}", proof))
    count = len(proofs)
    rest = count - len(issuers)
    named = ", ".join(issuers) + (f" and {rest} more" if rest else "")
    role = "led" if inv.is_lead else "joined"
    return HiddenLink(
        kind="trusted_co_investor",
        label=f"co-invested {count}× with {ref.name}",
        explanation=(
            f"{inv.name}, who {role} a round of {candidate.name}, invested alongside "
            f"{ref.name} in {count} other round{'s' if count > 1 else ''}: {named}."
        ),
        via_entity_id=inv.entity_id,
        target=target
        or LinkNode(entity_id=ref.entity_id, name=ref.name, entity_type="Organization"),
        count=count,
        trust=_weakest(trusts),
        nodes=nodes,
        edges=edges,
        facts=facts,
    )


def shared_investors(
    candidate: Candidate, graph: LinkGraph, trusted: Trusted, shortlist: list[Candidate]
) -> list[HiddenLink]:
    """One link per investor of the startup that also backs other startups on the list."""
    me = normalise_name(candidate.name)
    others = [
        c for c in shortlist if c.entity_id != candidate.entity_id and normalise_name(c.name) != me
    ]
    links: list[tuple[tuple[bool, int, bool], HiddenLink]] = []
    for inv in walk_order(candidate):
        backed = [(other, m) for other in others if (m := _backed_by(other, inv))]
        if not backed:
            continue
        start = _startup_branch(candidate, inv, graph)
        nodes, edges, trusts = start.nodes, start.edges, start.trusts
        facts: list[Fact] = []
        for other, (round_, their) in backed:
            node = graph.rounds.get(round_.entity_id) or {}
            via = _participation(node, their.entity_id) or {}
            issuer = _participation(node, other.entity_id) or {}
            if their.entity_id != inv.entity_id:  # same fund, another Cala entity
                _add(
                    nodes,
                    LinkNode(
                        entity_id=their.entity_id, name=their.name, entity_type="Organization"
                    ),
                )
            _add(nodes, _round_node(round_), _company(other))
            edges += [
                _edge(their.entity_id, round_.entity_id, via, "is_lead" if their.is_lead else None),
                _edge(other.entity_id, round_.entity_id, issuer, "ISSUER"),
            ]
            trusts += [_edge_trust(via), _edge_trust(issuer)]
            sources = _sources(via) + _sources(issuer)
            facts.append(
                Fact(
                    value=f"{other.name} · {round_.name}", trust=strongest(sources), sources=sources
                )
            )
        names = [other.name for other, _ in backed]
        count = len(names)
        shown = names[0] if count == 1 else f"{names[0]} and {count - 1} more"
        is_trusted = trusted.match(inv.entity_id, inv.name) is not None
        link = HiddenLink(
            kind="shared_investor",
            label=f"also backs {shown}",
            explanation=(
                f"{inv.name} backs {candidate.name} and also "
                f"{_join(names)}, {'another startup' if count == 1 else 'other startups'} "
                "on your list."
            ),
            via_entity_id=inv.entity_id,
            target=_company(backed[0][0]),
            count=count,
            trust=_weakest(trusts),
            nodes=nodes,
            edges=edges,
            facts=facts,
        )
        links.append(((is_trusted, count, inv.is_lead), link))
    links.sort(key=lambda pair: pair[0], reverse=True)
    return [link for _, link in links]


def _backed_by(other: Candidate, inv: Investor) -> tuple[Round, Investor] | None:
    """The newest round of `other` this investor took part in, matched by id or fund name."""
    key = normalise_name(inv.name)
    for round_ in newest_first(other.rounds):
        for their in round_.investors:
            if their.entity_id == inv.entity_id or (key and normalise_name(their.name) == key):
                return round_, their
    return None


def _company(c: Candidate) -> LinkNode:
    return LinkNode(entity_id=c.entity_id, name=c.name, entity_type="Company")


def _join(names: list[str]) -> str:
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


@dataclass
class _Branch:
    nodes: list[LinkNode]
    edges: list[LinkEdge]
    trusts: list[TrustLevel]


def _startup_branch(candidate: Candidate, inv: Investor, graph: LinkGraph) -> _Branch:
    """Startup -> its newest round with this investor <- the investor."""
    startup = _company(candidate)
    investor = LinkNode(
        entity_id=inv.entity_id,
        name=inv.name,
        entity_type=(graph.investors.get(inv.entity_id) or _Missing).entity_type,
    )
    nodes = [startup, investor]
    edges: list[LinkEdge] = []
    trusts: list[TrustLevel] = []
    rounds = newest_first(candidate.rounds)
    round_ = next(
        (r for r in rounds if any(i.entity_id == inv.entity_id for i in r.investors)), None
    )
    if round_ is not None:
        node = graph.rounds.get(round_.entity_id) or {}
        issuer = _participation(node, candidate.entity_id) or {}
        via = _participation(node, inv.entity_id) or {}
        nodes.insert(1, _round_node(round_))
        edges += [
            _edge(candidate.entity_id, round_.entity_id, issuer, "ISSUER"),
            _edge(inv.entity_id, round_.entity_id, via, "is_lead" if inv.is_lead else None),
        ]
        trusts += [_edge_trust(issuer), _edge_trust(via)]
    return _Branch(nodes, edges, trusts)


class _Missing:
    entity_type = "Organization"


def _round_node(round_: Round) -> LinkNode:
    return LinkNode(entity_id=round_.entity_id, name=round_.name, entity_type="FundingRound")


def _same(edge: dict[str, Any], entity_id: str, key: str) -> bool:
    return edge["id"] == entity_id or bool(key and normalise_name(edge.get("name")) == key)


def _funders(round_node: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        e
        for e in relationships(round_node, "incoming", PARTICIPATES)
        if str(edge_attr(e, "role") or "").upper() in FUNDING_ROLES
    ]


def _participation(round_node: dict[str, Any], entity_id: str) -> dict[str, Any] | None:
    return next(
        (e for e in relationships(round_node, "incoming", PARTICIPATES) if e["id"] == entity_id),
        None,
    )


def _issuer(round_node: dict[str, Any]) -> dict[str, Any] | None:
    return next(
        (
            e
            for e in relationships(round_node, "incoming", PARTICIPATES)
            if str(edge_attr(e, "role") or "").upper() == "ISSUER"
        ),
        None,
    )


def _round_name(round_node: dict[str, Any]) -> str:
    prop = (round_node.get("properties") or {}).get("name")
    value = prop.get("value") if isinstance(prop, dict) else None
    return value or round_node.get("name") or "Funding round"


def _node(edge: dict[str, Any], default_type: str) -> LinkNode:
    return LinkNode(
        entity_id=edge["id"],
        name=edge.get("name") or edge["id"],
        entity_type=edge.get("entity_type") or default_type,
    )


def _add(nodes: list[LinkNode], *new: LinkNode) -> None:
    for node in new:
        if all(n.entity_id != node.entity_id for n in nodes):
            nodes.append(node)


def _edge(source: str, target: str, edge: dict[str, Any], role: str | None = None) -> LinkEdge:
    if role is None and edge_attr(edge, "is_lead"):
        role = "is_lead"
    elif role is None:
        role = str(edge_attr(edge, "role") or "") or None
    return LinkEdge(source=source, target=target, relationship=PARTICIPATES, role=role)


def _sources(edge: dict[str, Any]) -> list[Source]:
    return [to_source(s) for s in (edge.get("properties") or {}).get("sources") or []]


def _edge_trust(edge: dict[str, Any]) -> TrustLevel:
    return strongest(_sources(edge))


def _weakest(trusts: list[TrustLevel]) -> TrustLevel:
    if not trusts:
        return UNRANKED
    return max(trusts, key=STRENGTH.index)


def _proof_fact(value: str, proof: _Proof) -> Fact:
    sources = _sources(proof.via_edge) + _sources(proof.other_edge)
    return Fact(value=value, trust=strongest(sources), sources=sources)

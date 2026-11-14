"""Proximity: how close a startup is, through funding rounds, to the investors the angel trusts.

The score is the sum of the paths it lists, so it can always be explained:
- ring 1: a trusted investor took part in one of the startup's own rounds;
- ring 2: an investor of the startup shared another round with a trusted investor (what the
  `trusted_co_investor` hidden link proves, `links.co_investments`).

Pure: it reads the candidate's rounds and the `LinkGraph` the walk already filled, and runs
again whenever the reference investors change. The weights are a first calibration
(decisions.md), all below.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

from app.cala.normalize import STRENGTH, UNRANKED, edge_attr, strongest
from app.discovery.build import build_round, normalise_name
from app.discovery.links import (
    FunderIndex,
    LinkGraph,
    Trusted,
    _edge_trust,
    _funders,
    _issuer,
    _participation,
    _proof_fact,
    _round_name,
    _sources,
    _weakest,
    co_investments,
    walk_order,
)
from app.models import (
    Candidate,
    Fact,
    Investor,
    Proximity,
    ProximityPath,
    ReferenceInvestor,
    Round,
    TrustLevel,
)
from app.signals.dates import parse_date

RING_WEIGHT = {1: 1.0, 2: 0.3}
LEAD_WEIGHT = 1.0
PARTICIPANT_WEIGHT = 0.6
RECENCY_HALF_LIFE_YEARS = 3.0
UNDATED_RECENCY = 0.5
SOURCE_WEIGHT: dict[TrustLevel, float] = {
    "filing": 1.0,
    "primary": 0.9,
    "press": 0.75,
    "aggregator": 0.6,
}
MAX_PATHS = 5
# One co-investor's shared rounds are one piece of evidence seen several times: without a cap
# a busy intermediary fills every slot and outweighs its own low selectivity.
MAX_PATHS_PER_INTERMEDIARY = 2


def proximity(
    candidate: Candidate,
    graph: LinkGraph,
    reference: list[ReferenceInvestor],
    *,
    today: date | None = None,
    index: FunderIndex | None = None,
) -> Proximity | None:
    """Score and strongest paths to the reference investors; None when there are none."""
    if not reference:
        return None
    today = today or date.today()
    trusted = Trusted(reference)
    index = index or FunderIndex(graph)
    paths = _ring_one(candidate, graph, trusted, today) + _ring_two(
        candidate, graph, trusted, today, index
    )
    paths.sort(key=lambda p: (-p.strength, p.ring, p.explanation))
    shown = paths[:MAX_PATHS]
    return Proximity(score=round(sum(p.strength for p in shown), 4), paths=shown)


def attach_proximity(
    candidates: list[Candidate],
    graph: LinkGraph,
    reference: list[ReferenceInvestor],
    *,
    today: date | None = None,
) -> list[Candidate]:
    index = FunderIndex(graph)
    return [
        c.model_copy(update={"proximity": proximity(c, graph, reference, today=today, index=index)})
        for c in candidates
    ]


def role_weight(is_lead: bool) -> float:
    return LEAD_WEIGHT if is_lead else PARTICIPANT_WEIGHT


def recency_weight(round_date: date | None, today: date) -> float:
    if round_date is None:
        return UNDATED_RECENCY
    years = max((today - round_date).days, 0) / 365.25
    return 0.5 ** (years / RECENCY_HALF_LIFE_YEARS)


def selectivity(rounds_in_graph: int) -> float:
    """A hub that shares rounds with everyone says little about any one of them."""
    return 1 / math.log2(2 + rounds_in_graph)


@dataclass
class _Leg:
    """An investor's part in one of the startup's own rounds, with what proves it."""

    round_: Round
    is_lead: bool
    recency: float
    trust: TrustLevel
    fact: Fact

    @property
    def weight(self) -> float:
        return role_weight(self.is_lead) * self.recency * SOURCE_WEIGHT[self.trust]


def _leg(candidate: Candidate, round_: Round, inv: Investor, graph: LinkGraph, today: date) -> _Leg:
    recency = recency_weight(parse_date(str(round_.date.value or "")), today)
    node = graph.rounds.get(round_.entity_id)
    if node is None:
        # Fixture candidates and rounds the walk did not keep have no raw edges: the round's
        # date is then the only sourced evidence of it.
        trust = round_.date.trust if round_.date.trust in STRENGTH else UNRANKED
        return _Leg(round_, inv.is_lead, recency, trust, round_.date)
    issuer = _participation(node, candidate.entity_id) or _issuer(node) or {}
    via = _participation(node, inv.entity_id) or {}
    sources = _sources(via) + _sources(issuer)
    fact = Fact(
        value=f"{candidate.name} · {round_.name}", trust=strongest(sources), sources=sources
    )
    trust = _weakest([_edge_trust(issuer), _edge_trust(via)])
    return _Leg(round_, inv.is_lead, recency, trust, fact)


def _ring_one(
    candidate: Candidate, graph: LinkGraph, trusted: Trusted, today: date
) -> list[ProximityPath]:
    # One path per round and trusted fund: two Cala entities of one fund in the same round
    # ("Y Combinator", "Y Combinator W24") are one investment, counted at its strongest.
    best: dict[tuple[str, str], tuple[_Leg, ReferenceInvestor, str]] = {}
    for round_ in candidate.rounds:
        for inv, verb in [(i, _verb(i.is_lead)) for i in round_.investors] + _grants(round_, graph):
            ref = trusted.match(inv.entity_id, inv.name)
            if ref is None:
                continue
            leg = _leg(candidate, round_, inv, graph, today)
            key = (round_.entity_id, ref.entity_id)
            if key not in best or leg.weight > best[key][0].weight:
                best[key] = (leg, ref, verb)
    return [
        ProximityPath(
            ring=1,
            strength=round(RING_WEIGHT[1] * leg.weight, 4),
            explanation=(
                f"{ref.name} {verb} {candidate.name}'s "
                f"{leg.round_.name}{_when(leg.round_.date.value)}."
            ),
            facts=[leg.fact],
        )
        for leg, ref, verb in best.values()
    ]


def _grants(round_: Round, graph: LinkGraph) -> list[tuple[Investor, str]]:
    """Grantors of the round, read from the raw node: the reverse walk follows a trusted
    fund's grants (FIRSTPICK), but a round's investors leave grantors out because most are
    public agencies that would flood links and suggestions."""
    node = graph.rounds.get(round_.entity_id)
    if node is None:
        return []
    return [
        (
            Investor(
                entity_id=e["id"],
                name=e.get("name") or e["id"],
                is_lead=bool(edge_attr(e, "is_lead")),
                role="investor",
            ),
            "gave a grant in",
        )
        for e in _funders(node)
        if str(edge_attr(e, "role") or "").upper() == "GRANTOR"
    ]


def _ring_two(
    candidate: Candidate, graph: LinkGraph, trusted: Trusted, today: date, index: FunderIndex
) -> list[ProximityPath]:
    paths: list[ProximityPath] = []
    for inv in walk_order(candidate):
        if trusted.match(inv.entity_id, inv.name):
            continue
        shared = co_investments(candidate, inv, graph, trusted, index)
        if not shared:
            continue
        leg = _strongest_leg(candidate, inv, graph, today)
        selective = selectivity(len(index.rounds_of(inv.entity_id, inv.name)))
        through: list[ProximityPath] = []
        for ref, proofs in shared:
            for proof in proofs:
                node = graph.rounds[proof.round_id]
                other_date = build_round(node).date.value
                # The path is as stale as its oldest round and as sure as its weakest edge.
                recency = min(leg.recency, recency_weight(parse_date(str(other_date or "")), today))
                trust = _weakest(
                    [leg.trust, _edge_trust(proof.via_edge), _edge_trust(proof.other_edge)]
                )
                strength = (
                    RING_WEIGHT[2]
                    * role_weight(leg.is_lead)
                    * recency
                    * SOURCE_WEIGHT[trust]
                    * selective
                )
                issuer = _issuer(node)
                issuer_name = issuer.get("name") if issuer else None
                round_name = _round_name(node)
                through.append(
                    ProximityPath(
                        ring=2,
                        strength=round(strength, 4),
                        explanation=(
                            f"{inv.name}, who {_verb(leg.is_lead)} {candidate.name}'s "
                            f"{leg.round_.name}, invested alongside {ref.name} in "
                            f"{issuer_name or 'an unnamed company'}'s {round_name}"
                            f"{_when(other_date)}."
                        ),
                        facts=[
                            leg.fact,
                            _proof_fact(
                                f"{issuer_name or 'Unnamed company'} · {round_name}", proof
                            ),
                        ],
                    )
                )
        through.sort(key=lambda p: -p.strength)
        paths += through[:MAX_PATHS_PER_INTERMEDIARY]
    return paths


def _strongest_leg(candidate: Candidate, inv: Investor, graph: LinkGraph, today: date) -> _Leg:
    """The intermediary's own round that counts most: role, recency and source together."""
    key = normalise_name(inv.name)
    legs = [
        _leg(candidate, round_, their, graph, today)
        for round_ in candidate.rounds
        for their in round_.investors
        if their.entity_id == inv.entity_id or (key and normalise_name(their.name) == key)
    ]
    return max(legs, key=lambda leg: leg.weight)


def _verb(is_lead: bool) -> str:
    return "led" if is_lead else "joined"


def _when(value: object) -> str:
    parsed = parse_date(str(value or ""))
    return f" ({parsed.year})" if parsed else ""

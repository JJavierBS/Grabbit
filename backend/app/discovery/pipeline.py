"""Event attendees -> startup candidates with rounds, leads and signals.

Path from Cala's field guide: `Event` -> incoming `PARTICIPATES_IN_EVENT` -> each company
-> its `ISSUER` rounds -> participants with `is_lead` -> each lead's other rounds (for the
follow-on signal). Every call goes through `CalaClient`, so a second run is all cache.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any, Protocol

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
from app.discovery.filters import StartupRules, is_startup, matches_profile
from app.models import Candidate, Profile, ProfileFilters, ProfileStyle
from app.signals.core import Portfolio, SignalInputs, compute_signals, last_round

log = logging.getLogger(__name__)

SLUSH_2026 = "bc844d56-6ab4-452b-96bf-2661e86e592b"

COMPANY_PROPERTIES = [
    "name",
    "legal_name",
    "aliases",
    "website",
    "description",
    "founding_date",
    "headquarters_address",
    "operational_status",
    "employee_count_range",
    "total_funding",
    "total_funding_units",
    "funding_stage",
]
COMPANY_OUTGOING = ["PARTICIPATES_IN_FUNDING_ROUND", "OPERATES_IN_INDUSTRY", "HAS_DOMAIN_NAME"]
COMPANY_INCOMING = ["FOUNDED", "IS_CEO_OF", "IS_CTO_OF", "IS_VICEPRESIDENT_OF"]
ROUND_BODY = {
    "properties": [
        "name",
        "round_label",
        "instrument",
        "transaction_value",
        "transaction_value_units",
        "announcement_date",
        "event_date",
        "event_date__precision",
    ],
    "relationships": {"incoming": {"PARTICIPATES_IN_FUNDING_ROUND": {"limit": 100}}},
}
INVESTOR_BODY = {
    "properties": ["name", "website"],
    "relationships": {"outgoing": {"PARTICIPATES_IN_FUNDING_ROUND": {"limit": 100}}},
}


class Cala(Protocol):
    async def introspect(self, entity_id: str) -> dict[str, Any]: ...
    async def retrieve(self, entity_id: str, body: dict[str, Any] | None = None) -> dict: ...


def neutral_profile(event_id: str | None = None) -> Profile:
    """No filters, no reference investors: every startup at the event (for `make warm`)."""
    return Profile(
        version=0,
        event_id=event_id,
        thesis="",
        filters=ProfileFilters(stages=[], sectors_in=[], sectors_out=[], countries=[]),
        reference_investors=[],
        style=ProfileStyle(length="medium", detail="plain", language="en", sections=[]),
        cadence="event",
        alert_threshold="medium",
        instructions="",
        updated_at=datetime.now(UTC),
    )


@dataclass
class Limits:
    page_size: int = 100
    max_attendees: int | None = None
    max_rounds_per_company: int = 10
    max_lead_rounds: int = 15
    rules: StartupRules = field(default_factory=StartupRules)


@dataclass
class DiscoveryStats:
    attendees: int = 0
    companies: int = 0
    startups: int = 0
    candidates: int = 0
    skipped: int = 0


@dataclass
class DiscoveryResult:
    candidates: list[Candidate]
    stats: DiscoveryStats
    raw: dict[str, dict[str, Any]] = field(default_factory=dict)


async def get_candidates(
    client: Cala,
    profile: Profile,
    today: date | None = None,
    limits: Limits | None = None,
) -> DiscoveryResult:
    """Startups attending the profile's event (default Slush 2026), filtered and scored."""
    today = today or date.today()
    limits = limits or Limits()
    stats = DiscoveryStats()
    raw: dict[str, dict[str, Any]] = {}

    stubs = await attendees(client, profile.event_id or SLUSH_2026, limits)
    stats.attendees = len(stubs)
    seen_names: set[str] = set()
    built: list[tuple[Candidate, dict[str, Any]]] = []
    for stub in stubs:
        if stub.get("entity_type") not in (None, "Company"):
            continue
        key = normalise_name(stub.get("name")) or stub["id"]
        if key in seen_names:
            continue  # brand and legal entity both attending
        seen_names.add(key)
        try:
            company = await fetch_company(client, stub["id"])
            stats.companies += 1
            raw[company["id"]] = company
            if not is_startup(company, today, limits.rules):
                continue
            stats.startups += 1
            rounds = []
            for rid in issuer_round_ids(company)[: limits.max_rounds_per_company]:
                node = await client.retrieve(rid, ROUND_BODY)
                raw[rid] = node
                rounds.append(build_round(node))
            built.append((build_candidate(company, rounds), company))
        except (CalaError, CalaCacheMiss) as err:
            stats.skipped += 1
            log.warning("skipping attendee %s: %s", stub.get("id"), err)

    candidates: list[Candidate] = []
    for candidate, company in built:
        if not matches_profile(candidate, profile):
            continue
        inputs = SignalInputs(
            reference_investors=profile.reference_investors,
            headcount_series=headcount_series(company),
            lead_portfolios=await lead_portfolios(client, candidate, limits, raw),
        )
        candidates.append(
            candidate.model_copy(update={"signals": compute_signals(candidate, inputs, today)})
        )
    stats.candidates = len(candidates)
    return DiscoveryResult(candidates=candidates, stats=stats, raw=raw)


async def attendees(client: Cala, event_id: str, limits: Limits) -> list[dict[str, Any]]:
    stubs: list[dict[str, Any]] = []
    offset = 0
    while True:
        body = {
            "relationships": {
                "incoming": {"PARTICIPATES_IN_EVENT": {"limit": limits.page_size, "offset": offset}}
            }
        }
        page = relationships(
            await client.retrieve(event_id, body), "incoming", "PARTICIPATES_IN_EVENT"
        )
        stubs.extend(page)
        if limits.max_attendees and len(stubs) >= limits.max_attendees:
            return stubs[: limits.max_attendees]
        if len(page) < limits.page_size:
            return stubs
        offset += limits.page_size


async def fetch_company(client: Cala, company_id: str) -> dict[str, Any]:
    """Introspect, then ask only for what this company has (docs/agents/cala.md)."""
    intro = await client.introspect(company_id)
    have = set(intro.get("properties") or [])
    rels = intro.get("relationships") or {}
    body: dict[str, Any] = {
        "properties": [p for p in COMPANY_PROPERTIES if p in have] or ["name"],
        "relationships": {
            "outgoing": {
                t: {"limit": 50} for t in COMPANY_OUTGOING if t in (rels.get("outgoing") or [])
            },
            "incoming": {
                t: {"limit": 20} for t in COMPANY_INCOMING if t in (rels.get("incoming") or [])
            },
        },
    }
    series = (intro.get("numerical_observations") or {}).get("ObservableProperty") or []
    employee_ids = [
        s["id"] for s in series if "employee" in f"{s.get('name', '')} {s.get('code', '')}".lower()
    ]
    if employee_ids:
        body["numerical_observations"] = {"ObservableProperty": employee_ids}
    return await client.retrieve(company_id, body)


async def lead_portfolios(
    client: Cala, candidate: Candidate, limits: Limits, raw: dict[str, dict[str, Any]]
) -> dict[str, Portfolio]:
    """The last round's lead and, per company it backed, the dates it took part."""
    round_ = last_round(candidate)
    lead = next((i for i in round_.investors if i.is_lead), None) if round_ else None
    if lead is None:
        return {}
    try:
        investor = await client.retrieve(lead.entity_id, INVESTOR_BODY)
        raw[lead.entity_id] = investor
        portfolio: Portfolio = {}
        edges = relationships(investor, "outgoing", "PARTICIPATES_IN_FUNDING_ROUND")
        for edge in edges[: limits.max_lead_rounds]:
            if str(edge_attr(edge, "role") or "").upper() not in ("INVESTOR", "LENDER"):
                continue
            node = await client.retrieve(edge["id"], ROUND_BODY)
            raw[edge["id"]] = node
            company_id = issuer_id(node)
            if company_id:
                when = build_round(node).date.value or edge_attr(edge, "event_date")
                portfolio.setdefault(company_id, []).append((when, True))
        return {lead.entity_id: portfolio}
    except (CalaError, CalaCacheMiss) as err:
        log.warning("no portfolio for lead %s: %s", lead.entity_id, err)
        return {}

"""Raw Cala nodes -> `Candidate`, `Round` and `Investor` (docs/agents/cala.md "The graph")."""

from __future__ import annotations

import re
from typing import Any

from app.cala.normalize import (
    edge_attr,
    not_published,
    observations,
    property_fact,
    relationships,
)
from app.models import Candidate, Fact, Investor, Round, Source

LEGAL_SUFFIXES = r"\b(oy|oyj|ab|as|aps|gmbh|ltd|limited|llc|inc|sa|sas|bv|nv|plc|co|corp)\b"


def normalise_name(name: str | None) -> str:
    text = re.sub(r"[^\w\s]", " ", (name or "").lower())
    text = re.sub(LEGAL_SUFFIXES, " ", text)
    return " ".join(text.split())


def build_round(round_node: dict[str, Any]) -> Round:
    props = round_node.get("properties") or {}
    date = property_fact(round_node, "event_date")
    if date.value is None:
        date = property_fact(round_node, "announcement_date")
    label = (props.get("round_label") or {}).get("value")
    name = (props.get("name") or {}).get("value") or round_node.get("name") or "Funding round"
    return Round(
        entity_id=round_node["id"],
        label=label,
        name=name,
        amount=property_fact(round_node, "transaction_value"),
        date=date,
        investors=participants(round_node),
    )


def participants(round_node: dict[str, Any]) -> list[Investor]:
    """Investors and lenders of a round, deduplicated; the issuer is not one of them."""
    seen: dict[str, Investor] = {}
    for edge in relationships(round_node, "incoming", "PARTICIPATES_IN_FUNDING_ROUND"):
        role = str(edge_attr(edge, "role") or "").upper()
        if role not in ("INVESTOR", "LENDER"):
            continue
        key = normalise_name(edge.get("name")) or edge["id"]
        investor = Investor(
            entity_id=edge["id"],
            name=edge.get("name") or edge["id"],
            is_lead=bool(edge_attr(edge, "is_lead")),
            role="lender" if role == "LENDER" else "investor",
        )
        if key in seen:
            # Same fund as Organization and Company: keep one, lead if either says so.
            seen[key].is_lead = seen[key].is_lead or investor.is_lead
        else:
            seen[key] = investor
    return list(seen.values())


def issuer_id(round_node: dict[str, Any]) -> str | None:
    for edge in relationships(round_node, "incoming", "PARTICIPATES_IN_FUNDING_ROUND"):
        if str(edge_attr(edge, "role") or "").upper() == "ISSUER":
            return edge["id"]
    return None


def issuer_round_ids(company: dict[str, Any]) -> list[str]:
    """Rounds the company raised; INVESTOR/LENDER edges are rounds it funded."""
    return [
        edge["id"]
        for edge in relationships(company, "outgoing", "PARTICIPATES_IN_FUNDING_ROUND")
        if str(edge_attr(edge, "role") or "").upper() == "ISSUER"
    ]


def headcount_fact(company: dict[str, Any]) -> Fact:
    fact = property_fact(company, "employee_count_range")
    value = fact.value
    if isinstance(value, list) and value:
        value = value[0] if len(value) == 1 else f"{value[0]}-{value[-1]}"
        return fact.model_copy(update={"value": value, "unit": "people"})
    return fact


def headcount_max(company: dict[str, Any]) -> int | None:
    value = property_fact(company, "employee_count_range").value
    if isinstance(value, list) and value:
        return int(value[-1])
    if isinstance(value, int | float):
        return int(value)
    return None


def headcount_series(company: dict[str, Any]) -> list[tuple[str, float, Source]]:
    return [(t, v, s) for t, v, s in observations(company, "employee_count") if v is not None]


def industries(company: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    for edge in relationships(company, "outgoing", "OPERATES_IN_INDUSTRY"):
        label = edge_attr(edge, "original_label") or edge.get("name")
        if label and label not in labels:
            labels.append(str(label))
    return labels


def build_candidate(company: dict[str, Any], rounds: list[Round]) -> Candidate:
    props = company.get("properties") or {}
    website = (props.get("website") or {}).get("value")
    name = (props.get("name") or {}).get("value") or company.get("name") or company["id"]
    hq = property_fact(company, "headquarters_address")
    if hq.value is None:
        hq = not_published()
    return Candidate(
        entity_id=company["id"],
        name=name,
        website=website,
        description=company.get("description"),
        founding_date=property_fact(company, "founding_date"),
        funding_stage=property_fact(company, "funding_stage"),
        headcount=headcount_fact(company),
        total_funding=property_fact(company, "total_funding"),
        hq=hq,
        industries=industries(company),
        rounds=sorted(rounds, key=lambda r: str(r.date.value or ""), reverse=True),
    )

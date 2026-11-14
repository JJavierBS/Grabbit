"""Local filters: Cala has no server-side filtering (docs/agents/cala.md "Traversal flow")."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.discovery.build import headcount_max, issuer_round_ids
from app.models import Candidate, Profile
from app.signals.dates import parse_date


@dataclass(frozen=True)
class StartupRules:
    """What separates startups from the funds and corporates attending an event."""

    max_age_years: int = 15
    max_headcount: int = 500


def is_startup(company: dict[str, Any], today: date, rules: StartupRules = StartupRules()) -> bool:
    if company.get("entity_type") != "Company":
        return False
    props = company.get("properties") or {}
    status = (props.get("operational_status") or {}).get("value")
    if status and str(status).upper() != "ACTIVE":
        return False
    has_stage = (props.get("funding_stage") or {}).get("value") is not None
    if not has_stage and not issuer_round_ids(company):
        return False  # funds, corporates and bootstrapped firms: not a round to join
    founded = parse_date((props.get("founding_date") or {}).get("value"))
    if founded and today.year - founded.year > rules.max_age_years:
        return False
    size = headcount_max(company)
    return not (size is not None and size > rules.max_headcount)


def matches_profile(candidate: Candidate, profile: Profile) -> bool:
    """Profile filters; a filter on a field the candidate does not publish lets it pass."""
    f = profile.filters
    stage = candidate.funding_stage.value
    if f.stages and stage and str(stage).upper() not in {s.upper() for s in f.stages}:
        return False
    hq = str(candidate.hq.value or "").lower()
    if f.countries and hq and not any(c.lower() in hq for c in f.countries):
        return False
    labels = " ".join(candidate.industries).lower()
    if f.sectors_out and any(s.lower() in labels for s in f.sectors_out):
        return False
    if f.sectors_in and labels and not any(s.lower() in labels for s in f.sectors_in):
        return False
    size = candidate.headcount.value
    if f.headcount_max is not None and isinstance(size, int | float):
        return size <= f.headcount_max
    return True

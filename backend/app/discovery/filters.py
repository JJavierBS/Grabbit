"""Local filters: Cala has no server-side filtering (docs/agents/cala.md "Traversal flow")."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from app.discovery.build import headcount_max, issuer_round_ids
from app.geo import hq_in
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


EARLY_STAGES = {"pre_seed", "seed", "angel"}


def normalise_stage(stage: object) -> str:
    """'Pre-Seed', 'PRE_SEED' and 'pre seed' are the same stage."""
    return re.sub(r"[\s\-]+", "_", str(stage).strip().lower())


def wanted_stages(stages: list[str]) -> set[str]:
    wanted = {normalise_stage(s) for s in stages}
    if "early" in wanted:
        wanted |= EARLY_STAGES
    return wanted


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def sector_matches(sector: str, industries: list[str]) -> bool:
    """A sector matches a whole industry label or one of its words ('AI' never 'retail')."""
    target = sector.strip().lower()
    return any(target == label.lower() or target in _words(label) for label in industries)


def headcount_upper(value: object) -> float | None:
    """Upper bound of a headcount: 18, '18', or a range like '51-200' -> 200."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    numbers = re.findall(r"\d+", str(value or ""))
    return float(numbers[-1]) if numbers else None


def matches_profile(candidate: Candidate, profile: Profile) -> bool:
    """Profile filters; a filter on a field the candidate does not publish lets it pass."""
    f = profile.filters
    stage = candidate.funding_stage.value
    if f.stages and stage and normalise_stage(stage) not in wanted_stages(f.stages):
        return False
    hq = str(candidate.hq.value or "")
    if f.countries and hq and not hq_in(hq, f.countries):
        return False
    industries = candidate.industries
    if f.sectors_out and any(sector_matches(s, industries) for s in f.sectors_out):
        return False
    if f.sectors_in and industries and not any(sector_matches(s, industries) for s in f.sectors_in):
        return False
    size = headcount_upper(candidate.headcount.value)
    return f.headcount_max is None or size is None or size <= f.headcount_max

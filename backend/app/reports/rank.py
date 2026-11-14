"""Filter and order candidates by the profile."""

from app.models import Candidate, Profile
from app.reports.facts import last_round

EARLY = ("pre_seed", "pre-seed", "seed", "angel")


def rank(candidates: list[Candidate], profile: Profile) -> list[Candidate]:
    """Default order: a reference investor led a round, then joined one, then likely to raise."""
    kept = [c for c in candidates if _matches(c, profile)]
    refs = {r.entity_id for r in profile.reference_investors}
    return sorted(kept, key=lambda c: _key(c, refs))


def co_invest(c: Candidate, refs: set[str]) -> tuple[bool, bool]:
    """(a reference investor led a round, a reference investor joined a round)."""
    involved = [i for r in c.rounds for i in r.investors if i.entity_id in refs]
    return any(i.is_lead for i in involved), bool(involved)


def _key(c: Candidate, refs: set[str]) -> tuple:
    led, joined = co_invest(c, refs)
    likely = next((s.value for s in c.signals if s.kind == "likely_to_raise"), None)
    r = last_round(c)
    recency = str(r.date.value) if r and r.date.value else ""
    # Negated recency string sorts newest first inside each group.
    return (
        not led,
        not joined,
        likely is not True,
        not recency,
        [-ord(ch) for ch in recency],
        c.name,
    )


def _matches(c: Candidate, profile: Profile) -> bool:
    f = profile.filters
    industries = {i.lower() for i in c.industries}
    if any(s.lower() in industries for s in f.sectors_out):
        return False
    if f.sectors_in and not any(s.lower() in industries for s in f.sectors_in):
        return False
    if f.countries and c.hq.value is not None:
        if str(c.hq.value).lower() not in {x.lower() for x in f.countries}:
            return False
    if f.headcount_max is not None and isinstance(c.headcount.value, int | float):
        if c.headcount.value > f.headcount_max:
            return False
    if f.stages and c.funding_stage.value is not None:
        stage = str(c.funding_stage.value).lower()
        wanted = {s.lower() for s in f.stages}
        if stage not in wanted and not ("early" in wanted and stage in EARLY):
            return False
    return True

"""Filter and order candidates by the profile."""

from app.discovery.filters import matches_profile
from app.models import Candidate, Profile
from app.reports.facts import last_round


def rank(candidates: list[Candidate], profile: Profile) -> list[Candidate]:
    """Default order: a reference investor led a round, then joined one, then likely to raise."""
    # The same filters as discovery (app.discovery.filters), so the two never disagree.
    kept = [c for c in candidates if matches_profile(c, profile)]
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

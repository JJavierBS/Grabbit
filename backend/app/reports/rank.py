"""Filter and order candidates by the profile."""

from datetime import date

from app.discovery.filters import matches_profile
from app.discovery.links import LinkGraph
from app.discovery.proximity import proximity
from app.models import Candidate, Profile
from app.reports.facts import last_round


def rank(
    candidates: list[Candidate], profile: Profile, *, today: date | None = None
) -> list[Candidate]:
    """Default order: closest to the reference investors, then likely to raise, then newest."""
    # The same filters as discovery (app.discovery.filters), so the two never disagree.
    kept = [c for c in candidates if matches_profile(c, profile, today=today)]
    return sorted(kept, key=lambda c: _key(c, _proximity_score(c, profile, today)))


def co_invest(c: Candidate, refs: set[str]) -> tuple[bool, bool]:
    """(a reference investor led a round, a reference investor joined a round)."""
    involved = [i for r in c.rounds for i in r.investors if i.entity_id in refs]
    return any(i.is_lead for i in involved), bool(involved)


def _proximity_score(c: Candidate, profile: Profile, today: date | None) -> float:
    if not profile.reference_investors:
        return 0.0
    # Candidates that never went through discovery (fixtures) carry no proximity: their own
    # rounds still say which trusted investors backed them.
    found = c.proximity or proximity(c, LinkGraph(), profile.reference_investors, today=today)
    return found.score if found else 0.0


def _key(c: Candidate, score: float) -> tuple:
    likely = next((s.value for s in c.signals if s.kind == "likely_to_raise"), None)
    r = last_round(c)
    recency = str(r.date.value) if r and r.date.value else ""
    # Negated recency string sorts newest first inside each group.
    return (
        -score,
        likely is not True,
        not recency,
        [-ord(ch) for ch in recency],
        c.name,
    )

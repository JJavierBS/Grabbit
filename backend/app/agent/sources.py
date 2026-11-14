"""Inputs the agent reads from other teams' modules, behind one seam."""

import logging

from pydantic import TypeAdapter

from app import fixtures
from app.cala.client import CalaCacheMiss, CalaError
from app.discovery.pipeline import Limits, get_candidates
from app.models import Candidate, Profile
from app.references import remember, resolve_references
from app.runtime import open_cala
from app.signals.core import co_invest

log = logging.getLogger(__name__)

# The sample warmed and measured for the demo thesis (decisions.md 09:40); warm at least this.
MAX_ATTENDEES = 150


def fixture_candidates() -> list[Candidate]:
    return TypeAdapter(list[Candidate]).validate_python(fixtures.load_json("candidates.json"))


async def candidates_for(profile: Profile) -> list[Candidate]:
    """Startups at the profile's event from the Slush discovery pipeline (#23).

    Falls back to the fictional fixture candidates only when Cala, or its cache in replay
    mode, cannot list the event, so a cold laptop still demos instead of failing.
    """
    try:
        async with open_cala() as (client, _):
            limits = Limits(max_attendees=MAX_ATTENDEES)
            result = await get_candidates(client, profile, limits=limits)
            remember(result.investors)
            candidates = result.candidates
    except (CalaError, CalaCacheMiss) as err:
        log.warning("discovery unavailable, using fixture candidates: %s", err)
        candidates = fixture_candidates()
    return _with_resolved_co_invest(candidates, profile)


def _with_resolved_co_invest(candidates: list[Candidate], profile: Profile) -> list[Candidate]:
    """Recompute co-invest once names typed in chat are linked to Cala investors."""
    resolved = resolve_references(profile, candidates)
    if resolved is profile:
        return candidates
    return [
        c.model_copy(
            update={
                "signals": [
                    co_invest(c, resolved.reference_investors) if s.kind == "co_invest" else s
                    for s in c.signals
                ]
            }
        )
        for c in candidates
    ]

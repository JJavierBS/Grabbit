"""Inputs the agent reads from other teams' modules, behind one seam."""

import logging
from datetime import UTC, datetime, timedelta

from pydantic import TypeAdapter

from app import fixtures
from app.agent.progress import report_attendees
from app.cala.client import CalaCacheMiss, CalaError
from app.discovery.filters import matches_profile
from app.discovery.links import LinkGraph, attach_links
from app.discovery.pipeline import SLUSH_2026, Limits, get_candidates, neutral_profile
from app.models import Candidate, Profile
from app.references import remember, resolve_references
from app.runtime import open_cala
from app.signals.core import co_invest

log = logging.getLogger(__name__)

# The sample warmed and measured for the demo thesis (decisions.md 09:40); warm at least this.
MAX_ATTENDEES = 150


def event_walk_limits() -> Limits:
    """The limits of the event walk every chat turn starts with; `make warm` replays exactly
    this walk so the first turn on the demo never misses the cache (#119)."""
    return Limits(max_attendees=MAX_ATTENDEES)


def fixture_candidates() -> list[Candidate]:
    return TypeAdapter(list[Candidate]).validate_python(fixtures.load_json("candidates.json"))


# Walking an event is hundreds of Cala calls (serial, rate-limited when cold), and every chat
# turn and report rebuild needs it. One walk per event is kept, unfiltered, and each profile
# is applied on top; the TTL lets new Cala data in. The watcher re-reads its shortlist fresh.
DISCOVERY_TTL = timedelta(minutes=15)
_discoveries: dict[str, tuple[datetime, list[Candidate], LinkGraph]] = {}


def clear_discovery_cache() -> None:
    _discoveries.clear()


def _now() -> datetime:
    return datetime.now(UTC)


async def _event_candidates(event_id: str) -> tuple[list[Candidate], LinkGraph]:
    hit = _discoveries.get(event_id)
    if hit and _now() - hit[0] < DISCOVERY_TTL:
        return hit[1], hit[2]
    async with open_cala() as (client, _):
        result = await get_candidates(
            client,
            neutral_profile(event_id),
            limits=event_walk_limits(),
            on_progress=report_attendees,
        )
    remember(result.investors)
    _discoveries[event_id] = (_now(), result.candidates, result.links)
    return result.candidates, result.links


async def candidates_for(profile: Profile) -> list[Candidate]:
    """Startups at the profile's event from the Slush discovery pipeline (#23), filtered by
    the profile, with co-invest computed against its reference investors.

    Falls back to the fictional fixture candidates only when Cala, or its cache in replay
    mode, cannot list the event, so a cold laptop still demos instead of failing.
    """
    graph: LinkGraph | None = None
    try:
        found, graph = await _event_candidates(profile.event_id or SLUSH_2026)
        candidates = [c for c in found if matches_profile(c, profile)]
    except (CalaError, CalaCacheMiss) as err:
        log.warning("discovery unavailable, using fixture candidates: %s", err)
        candidates = fixture_candidates()
    return _with_resolved_references(candidates, profile, graph)


def _with_resolved_references(
    candidates: list[Candidate], profile: Profile, graph: LinkGraph | None = None
) -> list[Candidate]:
    """Co-invest and hidden links against the profile's reference investors, with names
    typed in chat linked to Cala investors. The cached walk is unfiltered and has no
    references, so both are recomputed here on the filtered shortlist."""
    resolved = resolve_references(profile, candidates)
    if graph is not None:
        # Shared-investor links point at other startups on this shortlist, so they follow it.
        candidates = attach_links(candidates, graph, resolved.reference_investors)
    if not resolved.reference_investors:
        return candidates
    return [
        c.model_copy(
            update={
                "signals": [co_invest(c, resolved.reference_investors)]
                + [s for s in c.signals if s.kind != "co_invest"]
            }
        )
        for c in candidates
    ]

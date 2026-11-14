"""Link reference investors named in chat to the Cala investors seen in candidates' rounds.

The agent stores a name it could not resolve as `entity_id = "unresolved:<name>"`
(`agent/tools.py`); signals, ranking, report text and the watcher compare entity ids, so
without this a trusted investor typed in chat would never match.
"""

from app.discovery.build import normalise_name
from app.models import Candidate, Profile, ReferenceInvestor

UNRESOLVED = "unresolved:"


def resolve_references(profile: Profile, candidates: list[Candidate]) -> Profile:
    """Profile whose unresolved reference investors carry the matching Cala entity id."""
    if not any(r.entity_id.startswith(UNRESOLVED) for r in profile.reference_investors):
        return profile
    known = {
        normalise_name(investor.name): investor.entity_id
        for candidate in candidates
        for round_ in candidate.rounds
        for investor in round_.investors
    }
    resolved = [_resolve(ref, known) for ref in profile.reference_investors]
    return profile.model_copy(update={"reference_investors": resolved})


def _resolve(ref: ReferenceInvestor, known: dict[str, str]) -> ReferenceInvestor:
    if not ref.entity_id.startswith(UNRESOLVED):
        return ref
    entity_id = known.get(normalise_name(ref.name))
    return ref.model_copy(update={"entity_id": entity_id}) if entity_id else ref

"""Where the facts in a chat reply come from (#141).

Since #118 the model writes plain prose without badge names, so the app says it instead:
each startup from the candidates that the reply names gets the sources of its Cala facts.
Computed from the `Fact`s, never from what the model claims.
"""

import re

from app.cala.normalize import STRENGTH
from app.models import Candidate, Fact, ReplySource, Source

MAX_STARTUPS = 6
# Shorter names ("AI", "Mo") match inside ordinary words and sentences.
MIN_NAME = 3
# Strongest first; web, unverified after Cala's own levels.
ORDER = [*STRENGTH, "cala_news", "web_unverified"]


def reply_sources(text: str, candidates: list[Candidate]) -> list[ReplySource]:
    """The startups the reply names, in the order it names them, with their facts' sources."""
    found: list[tuple[int, Candidate]] = []
    for c in candidates:
        at = _first_mention(text, c.name)
        if at is not None:
            found.append((at, c))
    found.sort(key=lambda pair: pair[0])
    out = []
    for _, c in found[:MAX_STARTUPS]:
        sources = _sources(_facts(c))
        if sources:
            out.append(ReplySource(entity_id=c.entity_id, name=c.name, sources=sources))
    return out


def _first_mention(text: str, name: str) -> int | None:
    # Cala names funds and companies by their vehicle: "Acme (Acme Labs Oy)" reads "Acme".
    for variant in dict.fromkeys([name, name.split(" (")[0]]):
        if len(variant) < MIN_NAME:
            continue
        hit = re.search(rf"(?<!\w){re.escape(variant)}(?!\w)", text, flags=re.IGNORECASE)
        if hit:
            return hit.start()
    return None


def _facts(c: Candidate) -> list[Fact]:
    facts = [c.founding_date, c.funding_stage, c.headcount, c.total_funding, c.hq]
    return facts + [f for r in c.rounds for f in (r.amount, r.date)]


def _sources(facts: list[Fact]) -> list[Source]:
    """Each source once, at the strongest level Cala gave it; values Cala lists without a
    source are credited to Cala itself at their own level. Unpublished values cite nothing."""
    best: dict[str, Source] = {}
    for fact in facts:
        if fact.value is None or fact.trust == "not_published":
            continue
        for source in fact.sources or [Source(name="Cala", rank=fact.trust)]:
            kept = best.get(source.name)
            if kept is None or _strength(source) < _strength(kept):
                best[source.name] = source
    return sorted(best.values(), key=lambda s: (_strength(s), s.name))


def _strength(source: Source) -> int:
    return ORDER.index(source.rank) if source.rank in ORDER else len(ORDER)

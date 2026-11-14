"""Whether a round participant is one of the angel's reference investors.

One fund is often several Cala entities (Company, Organization, a vehicle per region or
batch) while a `ReferenceInvestor` holds one entity id, so signals, ranking, report text and
the watcher all match through `Trusted`: by id or by fund name.
"""

from __future__ import annotations

import re
from functools import lru_cache

from app.models import ReferenceInvestor

LEGAL_SUFFIXES = frozenset(
    {"oy", "oyj", "ab", "as", "aps", "gmbh", "ltd", "limited", "llc", "inc", "sa", "sas", "bv"}
    | {"nv", "plc", "co", "corp"}
)


@lru_cache(maxsize=65536)  # called per round edge, per candidate and investor, every turn
def normalise_name(name: str | None) -> str:
    """Lowercase words without punctuation or trailing legal forms ("Acme Oy Ltd" -> "acme").

    Legal forms are dropped only at the end: inside a name they are words ("Same As Ventures").
    """
    words = re.sub(r"[^\w\s]", " ", (name or "").lower()).split()
    while len(words) > 1 and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)


class Trusted:
    """Reference investors matched by Cala id or by name: one fund is often several entities."""

    def __init__(self, reference: list[ReferenceInvestor]):
        self.by_id = {r.entity_id: r for r in reference}
        self.by_name = {normalise_name(r.name): r for r in reference if normalise_name(r.name)}

    def match(self, entity_id: str | None, name: str | None) -> ReferenceInvestor | None:
        if entity_id is not None and entity_id in self.by_id:
            return self.by_id[entity_id]
        key = normalise_name(name)
        if not key:
            return None
        if key in self.by_name:
            return self.by_name[key]
        # "500 Global" vs "500 Global (500 Emerging Europe)": same rule as app/references.py,
        # two words at least so one common word never matches.
        for ref_key, ref in self.by_name.items():
            short, long_ = sorted((key, ref_key), key=len)
            if len(short.split()) >= 2 and long_.startswith(f"{short} "):
                return ref
        return None

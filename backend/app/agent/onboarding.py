"""Pick the 2-3 bank questions (agent.md "Question bank") that best split the candidates."""

import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime

from app.models import Candidate, Profile

EARLY_STAGES = ("pre_seed", "pre-seed", "preseed", "seed", "angel")


@dataclass(frozen=True)
class Question:
    key: str
    text: str
    split: float
    """0 = asking tells us nothing about these candidates, 1 = halves them."""


def pick_questions(
    candidates: list[Candidate], profile: Profile, now: datetime | None = None, limit: int = 3
) -> list[Question]:
    now = now or datetime.now(UTC)
    builders = (_stage, _ticket, _investors, _industries, _team, _recency, _hq)
    questions = [q for build in builders if (q := build(candidates, profile, now)) and q.split > 0]
    questions.sort(key=lambda q: q.split, reverse=True)
    return questions[:limit]


def _balance(a: int, b: int) -> float:
    return 2 * min(a, b) / (a + b) if a + b else 0.0


def _stage(cs: list[Candidate], _p: Profile, _n: datetime) -> Question | None:
    stages = [str(c.funding_stage.value).lower() for c in cs if c.funding_stage.value]
    if not stages:
        return None
    early = sum(1 for s in stages if any(e in s for e in EARLY_STAGES))
    later = len(stages) - early
    return Question(
        "stage",
        f"Of the {len(cs)} startups that match, {early} are pre-seed or seed and {later} "
        "Series A or later. Which stage?",
        _balance(early, later),
    )


def _ticket(cs: list[Candidate], profile: Profile, _n: datetime) -> Question | None:
    if profile.filters.ticket is not None:
        return None
    amounts = [
        (float(r.amount.value), r.amount.unit or "")
        for c in cs
        for r in c.rounds
        if isinstance(r.amount.value, int | float) and r.amount.value > 0
    ]
    units = {u for _, u in amounts}
    if len(amounts) < 2 or len(units) != 1:
        return None
    low, high = min(a for a, _ in amounts), max(a for a, _ in amounts)
    if high < 3 * low:
        return None
    unit = units.pop()
    return Question(
        "ticket",
        f"Rounds here range from {money(low, unit)} to {money(high, unit)}. What ticket do you "
        "write?",
        0.6,
    )


def _investors(cs: list[Candidate], profile: Profile, _n: datetime) -> Question | None:
    if not profile.reference_investors:
        backers = Counter(
            i.name
            for c in cs
            for i in {inv.entity_id: inv for r in c.rounds for inv in r.investors}.values()
        )
        if not backers:
            return None
        top = [name for name, _ in backers.most_common(2)]
        return Question(
            "investors",
            f"Which investors do you trust? {' and '.join(top)} back the most attendees here.",
            0.5,
        )
    refs = {r.entity_id for r in profile.reference_investors}
    backed = sum(1 for c in cs if any(i.entity_id in refs for r in c.rounds for i in r.investors))
    names = ", ".join(r.name for r in profile.reference_investors)
    return Question(
        "investors",
        f"{backed} attendees are backed by {names}. Any other investors you trust?",
        0.3,
    )


def _industries(cs: list[Candidate], profile: Profile, _n: datetime) -> Question | None:
    if profile.filters.sectors_in or profile.filters.sectors_out:
        return None
    counts = Counter(i for c in cs for i in c.industries)
    if len(counts) < 2:
        return None
    (first, a), (second, b) = counts.most_common(2)
    return Question(
        "industries",
        f"Most matches are in {first} ({a}) and {second} ({b}). Keep both?",
        _balance(a, b) * 0.9,
    )


def _team(cs: list[Candidate], profile: Profile, _n: datetime) -> Question | None:
    if profile.filters.headcount_max is not None:
        return None
    sizes = [n for c in cs if (n := _headcount(c.headcount.value)) is not None]
    if len(sizes) < 2 or max(sizes) < 2 * min(sizes):
        return None
    small = sum(1 for n in sizes if n <= 20)
    return Question(
        "team",
        f"Teams range from {min(sizes)} to {max(sizes)} people. Prefer small teams?",
        _balance(small, len(sizes) - small) * 0.8,
    )


def _recency(cs: list[Candidate], _p: Profile, now: datetime) -> Question | None:
    last_dates = [d for c in cs if (d := _last_round(c)) is not None]
    if not last_dates:
        return None
    recent = sum(1 for d in last_dates if (now.year - d[0]) * 12 + now.month - d[1] <= 12)
    return Question(
        "recency",
        f"{recent} raised in the last 12 months and {len(last_dates) - recent} earlier. "
        "Startups that just raised, or ones that may raise soon?",
        _balance(recent, len(last_dates) - recent),
    )


def _hq(cs: list[Candidate], profile: Profile, _n: datetime) -> Question | None:
    if profile.filters.countries:
        return None
    counts = Counter(str(c.hq.value) for c in cs if c.hq.value)
    if len(counts) < 2:
        return None
    ((top, n),) = counts.most_common(1)
    return Question(
        "hq",
        f"{n} of {sum(counts.values())} are headquartered in {top}. Anywhere, or only some "
        "countries?",
        1 - n / sum(counts.values()),
    )


def money(value: float, unit: str) -> str:
    for size, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if value >= size:
            return f"{unit} {value / size:.3g}{suffix}".strip()
    return f"{unit} {value:.0f}".strip()


def _headcount(value: object) -> int | None:
    if isinstance(value, int | float):
        return int(value)
    if isinstance(value, str) and (nums := re.findall(r"\d+", value)):
        return int(nums[-1])
    return None


def _last_round(c: Candidate) -> tuple[int, int] | None:
    dates = []
    for r in c.rounds:
        if isinstance(r.date.value, str) and (m := re.match(r"(\d{4})(?:-(\d{2}))?", r.date.value)):
            dates.append((int(m.group(1)), int(m.group(2) or 6)))
    return max(dates) if dates else None

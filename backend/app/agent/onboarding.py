"""Pick the 2-3 bank questions (agent.md "Question bank") to ask after the first message."""

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass, replace
from datetime import UTC, datetime

from pydantic import BaseModel

from app.llm import LLM, LLMError
from app.models import Candidate, Profile

log = logging.getLogger(__name__)

EARLY_STAGES = ("pre_seed", "pre-seed", "preseed", "seed", "angel")


@dataclass(frozen=True)
class Question:
    key: str
    text: str
    split: float
    """0 = asking tells us nothing about these candidates, 1 = halves them."""
    options: tuple[tuple[str, str], ...] = ()
    """(label on the button, sentence sent to the agent), so a click answers it (#153)."""


def pick_questions(
    candidates: list[Candidate],
    profile: Profile,
    now: datetime | None = None,
    limit: int | None = 3,
) -> list[Question]:
    now = now or datetime.now(UTC)
    builders = (_stage, _ticket, _investors, _industries, _team, _recency, _hq)
    questions = [q for build in builders if (q := build(candidates, profile, now)) and q.split > 0]
    questions.sort(key=lambda q: q.split, reverse=True)
    return questions[:limit]


WORDING_SYSTEM = """You choose the questions a research agent asks an investor right after
their first message, and word them for this investor.
From the candidate questions, pick the 2 or 3 that matter most for what the investor said,
most important first. Skip what their message already answers.
Write each question and its options in the language of the investor's message, short and
natural, in your own words rather than the template's. Keep every number exactly as given and
add none. Keep each question's options, in the same order and with the same meaning: the label
goes on a button, the answer is the sentence sent for the investor when they click it, in the
first person. Use only keys from the candidates."""


class WordedOption(BaseModel):
    label: str
    answer: str


class WordedQuestion(BaseModel):
    key: str
    text: str
    options: list[WordedOption]


class WordedQuestions(BaseModel):
    questions: list[WordedQuestion]


async def word_questions(
    llm: LLM, message: str, bank: list[Question], limit: int = 3
) -> list[Question]:
    """The bank questions that fit `message` best, in its language; the top of the bank on failure.

    The model only picks and rewords: a question whose numbers or options changed keeps the
    bank's wording, so every number still comes from Cala.
    """
    if not bank:
        return []
    candidates = json.dumps(
        [
            {
                "key": q.key,
                "text": q.text,
                "options": [{"label": label, "answer": answer} for label, answer in q.options],
            }
            for q in bank
        ],
        ensure_ascii=False,
    )
    try:
        worded = await llm.generate(
            task="questions",
            system=WORDING_SYSTEM,
            prompt=f"Investor's message:\n{message}\n\nCandidate questions:\n{candidates}",
            schema=WordedQuestions,
            quick=True,
        )
    except LLMError as exc:
        log.info("question wording skipped: %s", exc)
        return bank[:limit]
    by_key = {q.key: q for q in bank}
    picked: list[Question] = []
    for w in worded.questions:
        q = by_key.pop(w.key, None)
        if q is None:
            continue
        picked.append(_reworded(q, w) or q)
        if len(picked) == limit:
            break
    return picked or bank[:limit]


def _reworded(q: Question, w: WordedQuestion) -> Question | None:
    options = tuple((o.label.strip(), o.answer.strip()) for o in w.options)
    if not w.text.strip() or len(options) != len(q.options):
        return None
    pairs = [(q.text, w.text), *zip(q.options, options, strict=True)]
    for before, after in pairs:
        if _numbers(before) != _numbers(after) or not all(after):
            return None
    return replace(q, text=w.text.strip(), options=options)


def _numbers(text: str | tuple[str, ...]) -> list[str]:
    """Digit runs in order of size: "€5.2M" and "5,2 M€" both read ["2", "5"]."""
    joined = text if isinstance(text, str) else " ".join(text)
    return sorted(re.findall(r"\d+", joined))


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
        (
            ("Pre-seed and seed", "Only pre-seed and seed startups."),
            ("Series A or later", "Only Series A or later."),
            ("Any stage", "Keep every stage."),
        ),
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
        (
            (
                f"Small, near {money(low, unit)}",
                f"I invest in small rounds, near {money(low, unit)}.",
            ),
            (
                f"Large, near {money(high, unit)}",
                f"I invest in larger rounds, near {money(high, unit)}.",
            ),
            ("Any size", "Round size does not matter to me."),
        ),
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
        options = [(name, f"I trust {name}.") for name in top]
        if len(top) == 2:
            options.append(("Both", f"I trust {top[0]} and {top[1]}."))
        return Question(
            "investors",
            f"Which investors do you trust? {' and '.join(top)} back the most attendees here.",
            0.5,
            tuple(options),
        )
    refs = {r.entity_id for r in profile.reference_investors}
    backed = sum(1 for c in cs if any(i.entity_id in refs for r in c.rounds for i in r.investors))
    names = ", ".join(r.name for r in profile.reference_investors)
    return Question(
        "investors",
        f"{backed} attendees are backed by {names}. Any other investors you trust?",
        0.3,
        (("Just these", "No other investors for now."),),
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
        (
            ("Keep both", f"Keep both {first} and {second}."),
            (f"Only {first}", f"Only {first}."),
            (f"Only {second}", f"Only {second}."),
        ),
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
        (
            ("Small teams, up to 20", "Prefer small teams, up to 20 people."),
            ("Any size", "Team size does not matter to me."),
        ),
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
        (
            ("Just raised", "Show me startups that raised in the last 12 months."),
            ("May raise soon", "Show me startups that may raise soon."),
            ("Both", "Show me both: recent raises and startups that may raise soon."),
        ),
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
        (
            ("Anywhere", "Any country is fine."),
            (f"Only {top}", f"Only startups headquartered in {top}."),
        ),
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

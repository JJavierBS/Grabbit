"""Graph signals v1, exactly as docs/agents/agent.md "Signals (v1)". Pure functions.

A signal whose inputs are missing returns `value=None` with an explanation of what is
missing; it never guesses. Signals are hints for the angel, never recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.models import Candidate, Fact, ReferenceInvestor, Round, Signal, Source
from app.signals.dates import months_between, parse_date

RAISE_WINDOW_MONTHS = (12, 30)
HEADCOUNT_GROWTH = 0.20
FOLLOW_ON_RATIO = 0.30
MIN_PORTFOLIO = 3

# company id -> that company's rounds as (date, did the investor take part)
Portfolio = dict[str, list[tuple[str | None, bool]]]


@dataclass
class SignalInputs:
    """Graph data beyond the candidate itself, gathered by the discovery pipeline."""

    reference_investors: list[ReferenceInvestor] = field(default_factory=list)
    headcount_series: list[tuple[str, float, Source]] = field(default_factory=list)
    lead_portfolios: dict[str, Portfolio] = field(default_factory=dict)


def last_round(candidate: Candidate) -> Round | None:
    dated = [r for r in candidate.rounds if parse_date(r.date.value)]
    if not dated:
        return None
    return max(dated, key=lambda r: parse_date(r.date.value))


def co_invest(candidate: Candidate, reference: list[ReferenceInvestor]) -> Signal:
    """Value: names of the reference investors in its rounds, leads first, then most recent
    (api.md `Signal.value` holds scalars only; the explanation carries round and role)."""
    label = "Co-invest with who you trust"
    if not reference:
        return _empty("co_invest", label, "No reference investors in the profile yet.")
    if not candidate.rounds:
        return _empty("co_invest", label, "No funding rounds published for this company.")
    trusted = {r.entity_id: r.name for r in reference}
    matches: list[tuple[bool, str, str, str]] = []  # (is_lead, date, investor, round)
    facts: list[Fact] = []
    for round_ in candidate.rounds:
        for inv in round_.investors:
            if inv.entity_id in trusted:
                matches.append(
                    (inv.is_lead, str(round_.date.value or ""), trusted[inv.entity_id], round_.name)
                )
                facts.append(round_.date)
    if not matches:
        return Signal(
            kind="co_invest",
            label=label,
            value=[],
            explanation="None of your reference investors took part in its rounds.",
            facts=[],
        )
    matches.sort(reverse=True)  # leads first, then the most recent round
    names = list(dict.fromkeys(m[2] for m in matches))
    parts = [f"{name} {'led' if lead else 'joined'} its {rnd}" for lead, _, name, rnd in matches]
    return Signal(
        kind="co_invest",
        label=label,
        value=names,
        explanation="; ".join(parts) + ".",
        facts=facts,
    )


def _empty(kind: str, label: str, explanation: str) -> Signal:
    return Signal(kind=kind, label=label, value=None, explanation=explanation, facts=[])  # type: ignore[arg-type]


def lead_follow_on(candidate: Candidate, portfolios: dict[str, Portfolio]) -> Signal:
    label = "Lead follows on"
    round_ = last_round(candidate)
    lead = next((i for i in round_.investors if i.is_lead), None) if round_ else None
    if lead is None:
        return _empty("lead_follow_on", label, "No lead investor known for its last round.")
    portfolio = {
        cid: rounds
        for cid, rounds in portfolios.get(lead.entity_id, {}).items()
        if cid != candidate.entity_id
    }
    if len(portfolio) < MIN_PORTFOLIO:
        return _empty(
            "lead_follow_on",
            label,
            f"{lead.name} has {len(portfolio)} other known portfolio companies; "
            f"{MIN_PORTFOLIO} are needed.",
        )
    followed = sum(1 for rounds in portfolio.values() if _followed_on(rounds))
    ratio = followed / len(portfolio)
    return Signal(
        kind="lead_follow_on",
        label=label,
        value=round(ratio, 2),
        explanation=(
            f"{lead.name} joined a later round in {followed} of {len(portfolio)} "
            "other portfolio companies."
        ),
        facts=[round_.date],
    )


def _followed_on(rounds: list[tuple[str | None, bool]]) -> bool:
    dated = sorted(
        ((parse_date(d), took_part) for d, took_part in rounds if parse_date(d)),
        key=lambda x: x[0],
    )
    first_in = next((i for i, (_, took_part) in enumerate(dated) if took_part), None)
    if first_in is None:
        return False
    return any(took_part for _, took_part in dated[first_in + 1 :])


def likely_to_raise(
    candidate: Candidate,
    headcount_series: list[tuple[str, float, Source]],
    follow_on: Signal,
    today: date,
) -> Signal:
    label = "Likely to raise soon"
    checks: list[str] = []
    passed = 0
    with_data = 0
    facts: list[Fact] = []

    round_ = last_round(candidate)
    if round_ is not None:
        with_data += 1
        months = months_between(parse_date(round_.date.value), today)
        low, high = RAISE_WINDOW_MONTHS
        ok = low <= months <= high
        passed += ok
        ago = f"Its {round_.name} was {_months(months)} ago"
        usual = f"the usual {low} to {high} months between rounds"
        if ok:
            checks.append(f"{ago}, inside {usual}.")
        elif months < low:
            checks.append(f"{ago}, sooner than {usual}.")
        else:
            checks.append(f"{ago}, past {usual}.")
        facts.append(round_.date)
    else:
        checks.append("No dated round is published.")

    growth = _growth_last_year(headcount_series, today)
    if growth is not None:
        rate, start, end, sources = growth
        with_data += 1
        ok = rate >= HEADCOUNT_GROWTH
        passed += ok
        team = f"The team went from {start:g} to {end:g} people in a year ({rate:+.0%})"
        bar = f"{HEADCOUNT_GROWTH:.0%} growth that often comes before a round"
        checks.append(f"{team}, {'above' if ok else 'under'} the {bar}.")
        facts.append(Fact(value=end, unit="people", trust=sources[-1].rank, sources=sources))
    else:
        checks.append("Team size history covers less than a year.")

    if follow_on.value is not None:
        with_data += 1
        ok = follow_on.value >= FOLLOW_ON_RATIO
        passed += ok
        share = f"{follow_on.value:.0%} of its other startups"
        checks.append(
            f"Its lead investor came back for a later round in {share}"
            f"{'' if ok else f', under {FOLLOW_ON_RATIO:.0%}'}."
        )
    else:
        checks.append("Whether its lead investor follows on is not known.")

    value = None if with_data < 2 else passed >= 2
    return Signal(
        kind="likely_to_raise",
        label=label,
        value=value,
        explanation=" ".join(checks),
        facts=facts,
    )


def _months(n: int) -> str:
    return "1 month" if n == 1 else f"{n} months"


def _growth_last_year(
    series: list[tuple[str, float, Source]], today: date
) -> tuple[float, float, float, list[Source]] | None:
    points = sorted(
        ((parse_date(t), v, s) for t, v, s in series if parse_date(t) and v is not None),
        key=lambda p: p[0],
    )
    if len(points) < 2:
        return None
    end_date, end_value, end_source = points[-1]
    old = [p for p in points if months_between(p[0], end_date) >= 12]
    # A stale latest point says nothing about "the last 12 months".
    if not old or months_between(end_date, today) > 6:
        return None
    start_date, start_value, start_source = old[-1]
    if not start_value:
        return None
    rate = (end_value - start_value) / start_value
    return rate, start_value, end_value, [start_source, end_source]


def compute_signals(candidate: Candidate, inputs: SignalInputs, today: date) -> list[Signal]:
    follow_on = lead_follow_on(candidate, inputs.lead_portfolios)
    return [
        co_invest(candidate, inputs.reference_investors),
        follow_on,
        likely_to_raise(candidate, inputs.headcount_series, follow_on, today),
    ]

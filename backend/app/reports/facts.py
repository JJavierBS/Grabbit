"""Render facts server-side, so no number in a report ever comes from the model."""

import re

from app.agent.onboarding import money
from app.models import Candidate, Fact, Round, Source

BADGES = {
    "filing": "Official filing",
    "primary": "Company or investor",
    "press": "Press",
    "aggregator": "Database",
    "cala_news": "Cala news",
    "web_unverified": "Web, unverified",
    "not_published": "Not published",
}
MONTHS = "January February March April May June July August September October November December"


def render(fact: Fact | None, *, badge: bool = True) -> str:
    if fact is None or fact.value is None or fact.trust == "not_published":
        return "not published"
    value = fact.value
    if isinstance(value, bool):
        text = "yes" if value else "no"
    elif isinstance(value, int | float) and fact.unit and len(fact.unit) == 3:
        text = money(float(value), fact.unit)
    elif isinstance(value, int | float):
        text = f"{value:g}" + (f" {fact.unit}" if fact.unit else "")
    elif isinstance(value, list):
        text = ", ".join(str(v) for v in value)
    else:
        text = _date(str(value), fact) or str(value).replace("_", " ")
    return f"{text} ({BADGES[fact.trust]})" if badge else text


def _date(value: str, fact: Fact) -> str | None:
    m = re.fullmatch(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", value)
    if not m:
        return None
    precision = fact.sources[0].date_precision if fact.sources else None
    year, month, day = m.groups()
    if precision == "year" or not month:
        return year
    name = MONTHS.split()[int(month) - 1]
    if precision == "month" or not day:
        return f"{name} {year}"
    return f"{int(day)} {name} {year}"


def render_date(source: Source) -> str | None:
    if not source.date:
        return None
    fact = Fact(value=source.date, trust=source.rank, sources=[source])
    return _date(source.date, fact)


def last_round(c: Candidate) -> Round | None:
    return max(c.rounds, key=lambda r: str(r.date.value or ""), default=None)


def placeholders(c: Candidate, *, badge: bool = True) -> dict[str, str]:
    """Values the model may cite as {name} in a paragraph about this candidate."""
    values = {
        "stage": render(c.funding_stage, badge=badge),
        "headcount": render(c.headcount, badge=badge),
        "total_funding": render(c.total_funding, badge=badge),
        "hq": render(c.hq, badge=badge),
        "founded": render(c.founding_date, badge=badge),
    }
    if r := last_round(c):
        lead = next((i.name for i in r.investors if i.is_lead), None)
        values |= {
            "last_round": r.name,
            "last_round_amount": render(r.amount, badge=badge),
            "last_round_date": render(r.date, badge=badge),
            "last_round_lead": lead or "not published",
            "last_round_co_investors": ", ".join(i.name for i in r.investors if not i.is_lead)
            or "none published",
        }
    return values

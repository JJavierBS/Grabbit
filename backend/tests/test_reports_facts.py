from app.agent.sources import fixture_candidates
from app.models import Fact, Source
from app.reports.facts import placeholders, render


def _fact(value, precision=None, unit=None, trust="filing"):
    source = Source(name="Register", rank=trust, date_precision=precision)
    return Fact(value=value, unit=unit, trust=trust, sources=[source])


def test_absent_fact_reads_not_published_never_zero():
    assert render(Fact.not_published()) == "not published"
    assert render(Fact(value=0, trust="not_published")) == "not published"


def test_dates_show_only_their_precision():
    assert render(_fact("2019-01-01", "year"), badge=False) == "2019"
    assert render(_fact("2024-05", "month"), badge=False) == "May 2024"
    assert render(_fact("2024-05-07", "day"), badge=False) == "7 May 2024"


def test_money_and_badge():
    assert render(_fact(2_000_000, unit="EUR", trust="press")) == "EUR 2M (Press)"
    assert render(_fact(14, trust="primary")) == "14 (Company or investor)"


def test_placeholders_use_the_latest_round():
    kiln = next(c for c in fixture_candidates() if c.entity_id == "cand-kiln")
    values = placeholders(kiln)
    assert values["last_round"] == "Seed"
    assert values["last_round_lead"] == "North Pine Ventures"
    assert values["last_round_date"] == "May 2024 (Official filing)"

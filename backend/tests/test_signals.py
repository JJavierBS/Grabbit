from datetime import date

from app.models import Candidate, Fact, Investor, ReferenceInvestor, Round, Source
from app.signals.core import (
    SignalInputs,
    co_invest,
    compute_signals,
    lead_follow_on,
    likely_to_raise,
)

TODAY = date(2026, 11, 14)
AURORA = ReferenceInvestor(entity_id="aurora", name="Aurora Ventures")
BALTIC = ReferenceInvestor(entity_id="baltic", name="Baltic Angels")
SRC = Source(name="LinkedIn", url="https://x.example", rank="aggregator")


def fact(value) -> Fact:
    return Fact(value=value, trust="press", sources=[])


def make_round(rid: str, when: str | None, investors: list[Investor], name="Seed") -> Round:
    return Round(
        entity_id=rid, name=name, amount=fact(1_000_000), date=fact(when), investors=investors
    )


def make_candidate(rounds: list[Round]) -> Candidate:
    nothing = Fact(value=None, trust="not_published")
    return Candidate(
        entity_id="startup",
        name="Northwind",
        founding_date=nothing,
        funding_stage=nothing,
        headcount=nothing,
        total_funding=nothing,
        hq=nothing,
        industries=[],
        rounds=rounds,
        signals=[],
    )


def lead(iid="aurora", name="Aurora Ventures") -> Investor:
    return Investor(entity_id=iid, name=name, is_lead=True, role="investor")


def member(iid="baltic", name="Baltic Angels") -> Investor:
    return Investor(entity_id=iid, name=name, is_lead=False, role="investor")


# co_invest


def test_co_invest_lists_leads_first_then_most_recent():
    candidate = make_candidate(
        [
            make_round("r1", "2023-01-10", [member("baltic")], name="Pre-Seed"),
            make_round("r2", "2024-11-01", [lead("aurora"), member("baltic")]),
        ]
    )
    signal = co_invest(candidate, [AURORA, BALTIC])
    assert signal.value == ["Aurora Ventures", "Baltic Angels"]
    assert signal.explanation == (
        "Aurora Ventures led its Seed; Baltic Angels joined its Seed; "
        "Baltic Angels joined its Pre-Seed."
    )


def test_co_invest_without_reference_investors_is_null():
    candidate = make_candidate([make_round("r1", "2024-01-01", [lead()])])
    assert co_invest(candidate, []).value is None


def test_co_invest_without_rounds_is_null():
    assert co_invest(make_candidate([]), [AURORA]).value is None


def test_co_invest_no_overlap_is_empty_not_null():
    candidate = make_candidate([make_round("r1", "2024-01-01", [lead("other", "Other")])])
    signal = co_invest(candidate, [AURORA])
    assert signal.value == []


# lead_follow_on

PORTFOLIO = {
    "aurora": {
        "a": [("2022-01-01", True), ("2023-06-01", True)],  # followed on
        "b": [("2022-01-01", True), ("2023-06-01", False)],  # did not
        "c": [("2021-01-01", False), ("2022-01-01", True), ("2024-01-01", True)],  # followed on
        "startup": [("2024-11-01", True), ("2025-11-01", True)],  # the candidate: excluded
    }
}


def test_lead_follow_on_ratio_excludes_the_candidate():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    signal = lead_follow_on(candidate, PORTFOLIO)
    assert signal.value == 0.67
    assert "2 of 3" in signal.explanation


def test_lead_follow_on_needs_three_companies():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    small = {"aurora": {"a": PORTFOLIO["aurora"]["a"], "b": PORTFOLIO["aurora"]["b"]}}
    assert lead_follow_on(candidate, small).value is None


def test_lead_follow_on_without_a_lead_is_null():
    candidate = make_candidate([make_round("r1", "2024-11-01", [member()])])
    assert lead_follow_on(candidate, PORTFOLIO).value is None


def test_lead_follow_on_uses_the_last_round():
    candidate = make_candidate(
        [
            make_round("r0", "2022-01-01", [lead("other", "Other")]),
            make_round("r1", "2024-11-01", [lead()]),
        ]
    )
    assert lead_follow_on(candidate, PORTFOLIO).value == 0.67


# likely_to_raise

GROWING = [("2025-09-01", 12, SRC), ("2026-10-01", 18, SRC)]
FLAT = [("2025-09-01", 18, SRC), ("2026-10-01", 18, SRC)]


def follow_on_signal(value):
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    signal = lead_follow_on(candidate, PORTFOLIO)
    return signal.model_copy(update={"value": value})


def test_likely_when_all_three_checks_pass():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])  # 24 months
    signal = likely_to_raise(candidate, GROWING, follow_on_signal(0.67), TODAY)
    assert signal.value is True
    assert signal.explanation.count("yes:") == 3


def test_two_of_three_is_enough():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    assert likely_to_raise(candidate, FLAT, follow_on_signal(0.67), TODAY).value is True


def test_one_of_three_is_false():
    candidate = make_candidate([make_round("r1", "2026-06-01", [lead()])])  # 5 months
    assert likely_to_raise(candidate, FLAT, follow_on_signal(0.67), TODAY).value is False


def test_round_window_edges():
    for when, expected in [("2025-11-14", True), ("2025-11-15", False), ("2024-05-14", True)]:
        candidate = make_candidate([make_round("r1", when, [lead()])])
        signal = likely_to_raise(candidate, GROWING, follow_on_signal(None), TODAY)
        assert signal.value is expected, when


def test_null_with_fewer_than_two_checks_with_data():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    signal = likely_to_raise(candidate, [], follow_on_signal(None), TODAY)
    assert signal.value is None
    assert signal.explanation.count("no data") == 2


def test_stale_or_short_headcount_history_counts_as_no_data():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead()])])
    short = [("2026-06-01", 10, SRC), ("2026-10-01", 18, SRC)]
    stale = [("2023-01-01", 10, SRC), ("2024-02-01", 18, SRC)]
    for series in (short, stale):
        assert likely_to_raise(candidate, series, follow_on_signal(None), TODAY).value is None


def test_year_precision_dates_are_understood():
    candidate = make_candidate([make_round("r1", "2024", [lead()])])  # Jan 2024: 34 months
    signal = likely_to_raise(candidate, GROWING, follow_on_signal(0.67), TODAY)
    assert "34 months" in signal.explanation
    assert signal.value is True


def test_compute_signals_returns_the_three_kinds():
    candidate = make_candidate([make_round("r1", "2024-11-01", [lead(), member()])])
    inputs = SignalInputs(
        reference_investors=[AURORA], headcount_series=GROWING, lead_portfolios=PORTFOLIO
    )
    signals = compute_signals(candidate, inputs, TODAY)
    assert [s.kind for s in signals] == ["co_invest", "lead_follow_on", "likely_to_raise"]
    assert signals[2].value is True

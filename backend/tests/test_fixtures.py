"""The fixtures feed the mocks and other teams' work for hours: pin what they must cover."""

from app import fixtures
from app.models import Fact


def _all_facts() -> list[Fact]:
    report = fixtures.latest_report()
    found: list[Fact] = []
    for candidate in report.candidates:
        found += [
            candidate.founding_date,
            candidate.funding_stage,
            candidate.headcount,
            candidate.total_funding,
            candidate.hq,
        ]
        for round_ in candidate.rounds:
            found += [round_.amount, round_.date]
        for signal in candidate.signals:
            found += signal.facts
    for alert in fixtures.alerts():
        found += alert.facts
    return found


def test_report_has_three_candidates_with_every_signal_kind():
    report = fixtures.latest_report()

    assert len(report.candidates) >= 3
    for candidate in report.candidates:
        assert {s.kind for s in candidate.signals} == {
            "co_invest",
            "lead_follow_on",
            "likely_to_raise",
        }
    assert any(s.value is None for c in report.candidates for s in c.signals)


def test_facts_cover_every_trust_level():
    levels = {fact.trust for fact in _all_facts()}

    assert levels == {
        "filing",
        "primary",
        "press",
        "aggregator",
        "web_unverified",
        "not_published",
    }


def test_not_published_facts_are_empty_never_zero():
    absent = [fact for fact in _all_facts() if fact.trust == "not_published"]

    assert absent
    assert all(fact.value is None and fact.sources == [] for fact in absent)


def test_trust_is_the_strongest_source_rank():
    for fact in _all_facts():
        if fact.sources:
            assert fact.trust in {source.rank for source in fact.sources}


def test_a_year_precision_date_exists():
    precisions = {source.date_precision for fact in _all_facts() for source in fact.sources}
    assert "year" in precisions


def test_every_round_has_a_lead():
    for candidate in fixtures.latest_report().candidates:
        for round_ in candidate.rounds:
            assert any(investor.is_lead for investor in round_.investors)


def test_report_sections_point_at_real_candidates():
    report = fixtures.latest_report()
    ids = {candidate.entity_id for candidate in report.candidates}

    for section in report.sections:
        assert set(section.candidate_ids) <= ids


def test_alerts_include_a_simulated_and_a_real_one():
    simulated = {alert.simulated for alert in fixtures.alerts()}
    assert simulated == {True, False}


def test_profile_history_is_newest_first():
    versions = [change.version for change in fixtures.profile_history()]

    assert versions == sorted(versions, reverse=True)
    assert versions[0] == fixtures.profile().version


def test_demo_events_are_valid_alert_payloads():
    assert fixtures.demo_event_names()
    assert fixtures.demo_event("missing") is None

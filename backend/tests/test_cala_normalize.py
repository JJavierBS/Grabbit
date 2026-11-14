from app.cala.normalize import (
    edge_attr,
    edge_fact,
    observations,
    property_fact,
    relationships,
    to_fact,
)
from tests.conftest import load_cala


def test_absent_property_is_not_published_never_zero():
    company = load_cala("company_startup")
    fact = property_fact(company, "annual_recurring_revenue")
    assert fact.value is None
    assert fact.trust == "not_published"
    assert fact.sources == []


def test_sourced_zero_is_kept_as_zero():
    fact = to_fact(
        0, [{"name": "Company", "document": "https://x.example", "source_rank": "PRIMARY"}]
    )
    assert fact.value == 0
    assert fact.trust == "primary"


def test_strongest_source_sets_trust():
    company = load_cala("company_startup")
    fact = property_fact(company, "legal_name")
    assert fact.trust == "filing"
    assert {s.rank for s in fact.sources} == {"filing", "aggregator"}


def test_both_document_shapes_give_a_url():
    company = load_cala("company_startup")
    urls = [s.url for s in property_fact(company, "legal_name").sources]
    assert urls == [
        "https://tietopalvelu.ytj.fi/yritys/0000000-1",
        "https://api.example-aggregator.com/org/northwind",
    ]


def test_each_source_rank_maps_to_its_trust_level():
    company = load_cala("company_startup")
    assert property_fact(company, "name").trust == "primary"
    assert property_fact(company, "funding_stage").trust == "press"
    assert property_fact(company, "total_funding").trust == "aggregator"


def test_value_without_sources_never_claims_more_than_aggregator():
    company = load_cala("company_startup")
    fact = property_fact(company, "website")
    assert fact.value == "northwind.example"
    assert fact.trust == "aggregator"


def test_units_and_precision_are_picked_up():
    company = load_cala("company_startup")
    funding = property_fact(company, "total_funding")
    assert (funding.value, funding.unit) == (4500000, "EUR")
    founded = property_fact(company, "founding_date")
    assert founded.sources[0].date_precision == "year"
    round_ = load_cala("round_seed")
    assert property_fact(round_, "event_date").sources[0].date_precision == "month"


def test_edge_attributes_and_edge_facts():
    company = load_cala("company_startup")
    rounds = relationships(company, "outgoing", "PARTICIPATES_IN_FUNDING_ROUND")
    assert [edge_attr(r, "role") for r in rounds] == ["ISSUER", "INVESTOR"]
    date = edge_fact(rounds[0], "event_date")
    assert (date.value, date.trust) == ("2024-11-15", "press")
    assert edge_fact(rounds[0], "valid_until").trust == "not_published"


def test_observations_by_code_sorted_oldest_first():
    company = load_cala("company_startup")
    points = observations(company, "employee_count")
    assert [(t, v) for t, v, _ in points] == [("2025-09-01", 12), ("2026-10-01", 18)]
    assert points[0][2].url == "https://aggregator.example/n/2025"

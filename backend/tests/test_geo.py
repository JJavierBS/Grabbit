from app.geo import hq_in


def test_country_matches_the_country_part_of_a_cala_hq():
    assert hq_in("Copenhagen, Denmark", ["Denmark"])
    assert not hq_in("San Francisco, United States", ["Denmark"])


def test_a_region_expands_to_its_countries():
    assert hq_in("Helsinki, Finland", ["Europe"])
    assert hq_in("London, United Kingdom", ["europe"])
    assert hq_in("Oslo, Norway", ["Nordics"])
    assert not hq_in("San Francisco, United States", ["Europe"])


def test_a_city_matches_too():
    assert hq_in("Helsinki, Finland", ["Helsinki"])
    assert not hq_in("Russia", ["US"])

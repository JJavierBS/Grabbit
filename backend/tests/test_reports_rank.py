from app.models import Profile, ReferenceInvestor
from app.reports.rank import rank
from tests.helpers import fixture_candidates


def _names(profile):
    return [c.name for c in rank(fixture_candidates(), profile)]


def test_reference_investor_leads_come_first(now):
    profile = Profile(
        updated_at=now,
        reference_investors=[ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")],
    )
    names = _names(profile)
    assert set(names[:2]) == {"Ledgerly", "Brikk"}


def test_lead_ranks_above_participant(now):
    profile = Profile(
        updated_at=now,
        reference_investors=[ReferenceInvestor(entity_id="inv-north-pine", name="North Pine")],
    )
    names = _names(profile)
    assert names[0] == "Kiln Analytics"
    assert names.index("Ledgerly") < names.index("Mossa Health")


def test_without_references_newest_round_first(now):
    assert _names(Profile(updated_at=now))[0] == "Saunaverse"


def test_filters_drop_sectors_countries_and_big_teams(now):
    profile = Profile(updated_at=now)
    profile.filters.sectors_out = ["b2c"]
    assert "Mossa Health" not in _names(profile) and "Saunaverse" not in _names(profile)
    profile.filters.countries = ["Finland"]
    assert set(_names(profile)) == {"Kiln Analytics", "Tundra Grid"}


def test_unknown_headcount_is_kept_by_headcount_filter(now):
    profile = Profile(updated_at=now)
    profile.filters.headcount_max = 20
    names = _names(profile)
    assert "Mossa Health" in names and "Ledgerly" not in names

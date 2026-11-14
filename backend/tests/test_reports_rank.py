from app.agent.sources import fixture_candidates
from app.models import ReferenceInvestor
from app.reports.rank import rank
from app.store.profile import default_profile


def _names(profile):
    return [c.name for c in rank(fixture_candidates(), profile)]


def test_reference_investor_leads_come_first(now):
    profile = default_profile(now).model_copy(
        update={
            "reference_investors": [ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")]
        }
    )
    names = _names(profile)
    assert set(names[:2]) == {"Ledgerly", "Brikk"}


def test_lead_ranks_above_participant(now):
    profile = default_profile(now).model_copy(
        update={
            "reference_investors": [
                ReferenceInvestor(entity_id="inv-north-pine", name="North Pine")
            ]
        }
    )
    names = _names(profile)
    assert names[0] == "Kiln Analytics"
    assert names.index("Ledgerly") < names.index("Mossa Health")


def test_without_references_newest_round_first(now):
    assert _names(default_profile(now))[0] == "Saunaverse"


def test_filters_drop_sectors_countries_and_big_teams(now):
    profile = default_profile(now)
    profile.filters.sectors_out = ["b2c"]
    assert "Mossa Health" not in _names(profile) and "Saunaverse" not in _names(profile)
    profile.filters.countries = ["Finland"]
    assert set(_names(profile)) == {"Kiln Analytics", "Tundra Grid"}


def test_unknown_headcount_is_kept_by_headcount_filter(now):
    profile = default_profile(now)
    profile.filters.headcount_max = 20
    names = _names(profile)
    assert "Mossa Health" in names and "Ledgerly" not in names


def _with(candidate, **update):
    return candidate.model_copy(update=update)


def test_rank_and_discovery_apply_the_same_filters(now):
    from app.discovery.filters import matches_profile

    profile = default_profile(now)
    profile.filters.stages = ["early"]
    profile.filters.sectors_in = ["AI"]
    for c in fixture_candidates():
        assert (c in rank([c], profile)) == matches_profile(c, profile), c.name


def test_rank_keeps_a_startup_that_publishes_no_industries(now):
    profile = default_profile(now)
    profile.filters.sectors_in = ["ai"]
    bare = _with(fixture_candidates()[0], industries=[])
    assert rank([bare], profile) == [bare]


def test_rank_sector_ai_never_matches_retail(now):
    profile = default_profile(now)
    profile.filters.sectors_in = ["AI"]
    retail = _with(fixture_candidates()[0], industries=["retail"])
    assert rank([retail], profile) == []

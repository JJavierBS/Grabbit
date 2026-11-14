from app.agent.sources import fixture_candidates
from app.models import Proximity, ReferenceInvestor, Signal
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


NEWEST_FIRST = ["Saunaverse", "Mossa Health", "Ledgerly", "Kiln Analytics", "Brikk", "Tundra Grid"]


def _close(candidate, score):
    return candidate.model_copy(update={"proximity": Proximity(score=score, paths=[])})


def test_without_references_the_order_ignores_proximity(now):
    profile = default_profile(now)
    assert _names(profile) == NEWEST_FIRST
    scored = [_close(c, n) for n, c in enumerate(fixture_candidates())]
    assert [c.name for c in rank(scored, profile)] == NEWEST_FIRST


def test_with_references_the_highest_proximity_score_comes_first(now):
    profile = default_profile(now).model_copy(
        update={"reference_investors": [ReferenceInvestor(entity_id="inv-none", name="Nobody")]}
    )
    scores = {"Tundra Grid": 0.9, "Brikk": 0.15}
    scored = [_close(c, scores.get(c.name, 0.0)) for c in fixture_candidates()]
    names = [c.name for c in rank(scored, profile)]
    assert names == [
        "Tundra Grid",
        "Brikk",
        "Saunaverse",
        "Mossa Health",
        "Ledgerly",
        "Kiln Analytics",
    ]


def test_equal_proximity_falls_back_to_likely_to_raise_then_recency(now):
    profile = default_profile(now).model_copy(
        update={"reference_investors": [ReferenceInvestor(entity_id="inv-none", name="Nobody")]}
    )
    likely = Signal(kind="likely_to_raise", label="Likely", value=True, explanation="", facts=[])
    scored = [
        _close(c, 0.5).model_copy(update={"signals": [likely] if c.name == "Brikk" else []})
        for c in fixture_candidates()
    ]
    names = [c.name for c in rank(scored, profile)]
    assert names == ["Brikk"] + [n for n in NEWEST_FIRST if n != "Brikk"]


def test_candidates_without_proximity_are_scored_from_their_own_rounds(now):
    profile = default_profile(now).model_copy(
        update={
            "reference_investors": [
                ReferenceInvestor(entity_id="unresolved:fjord capital", name="Fjord Capital")
            ]
        }
    )
    # Ledgerly's Fjord-led round is newer than Brikk's; nobody else has Fjord.
    assert _names(profile)[:3] == ["Ledgerly", "Brikk", "Saunaverse"]


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

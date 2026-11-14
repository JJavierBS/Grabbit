import math
from datetime import date

import pytest

from app.discovery.build import build_candidate, build_round
from app.discovery.links import LinkGraph
from app.discovery.proximity import MAX_PATHS, attach_proximity, proximity
from app.models import ReferenceInvestor
from tests.conftest import load_cala

TODAY = date(2026, 11, 14)
THREE_YEARS_AGO = "2023-11-14"
TRUSTED = ReferenceInvestor(entity_id="t", name="Trusted Fund")


def party(entity_id, name, role="INVESTOR", lead=False, rank="FILING"):
    return {
        "id": entity_id,
        "name": name,
        "entity_type": "Organization",
        "properties": {
            "role": role,
            "is_lead": lead,
            "sources": [
                {
                    "name": rank.lower(),
                    "document": f"https://{entity_id}.example",
                    "source_rank": rank,
                }
            ],
        },
    }


def round_node(rid, issuer, investors, date_="2026-11-14", issuer_rank="FILING"):
    properties = {"name": {"value": f"Seed {rid}", "sources": []}}
    if date_:
        properties["event_date"] = {"value": date_, "sources": []}
    return {
        "id": rid,
        "name": f"Seed {rid}",
        "entity_type": "FundingRound",
        "properties": properties,
        "relationships": {
            "incoming": {
                "PARTICIPATES_IN_FUNDING_ROUND": [
                    party(issuer, issuer.title(), role="ISSUER", rank=issuer_rank),
                    *investors,
                ]
            }
        },
    }


def startup(*own_rounds, others=()):
    """The candidate "startup" with its own rounds, and the graph holding every round."""
    candidate = build_candidate(
        {"id": "startup", "name": "Startup"}, [build_round(r) for r in own_rounds]
    )
    graph = LinkGraph(rounds={r["id"]: r for r in (*own_rounds, *others)})
    return candidate, graph


def score(*own_rounds, others=(), reference=(TRUSTED,)):
    candidate, graph = startup(*own_rounds, others=others)
    return proximity(candidate, graph, list(reference), today=TODAY).score


def trusted(**kwargs):
    return party("t", "Trusted Fund", **kwargs)


def middle(**kwargs):
    return party("m", "Middle VC", **kwargs)


def test_no_reference_investors_means_no_proximity():
    candidate, graph = startup(round_node("r1", "startup", [trusted(lead=True)]))
    assert proximity(candidate, graph, [], today=TODAY) is None
    assert attach_proximity([candidate], graph, [], today=TODAY)[0].proximity is None


def test_no_path_scores_zero():
    candidate, graph = startup(round_node("r1", "startup", [middle(lead=True)]))
    found = proximity(candidate, graph, [TRUSTED], today=TODAY)
    assert found.score == 0 and found.paths == []


def test_a_lead_counts_more_than_a_participant():
    assert score(round_node("r1", "startup", [trusted(lead=True)])) == 1.0
    assert score(round_node("r1", "startup", [trusted()])) == 0.6


def test_a_round_loses_half_its_weight_every_three_years():
    three_years = score(round_node("r1", "startup", [trusted(lead=True)], THREE_YEARS_AGO))
    six_years = score(round_node("r1", "startup", [trusted(lead=True)], "2020-11-14"))
    # Leap days move the exact halving date by a day.
    assert three_years == pytest.approx(0.5, abs=1e-3)
    assert six_years == pytest.approx(0.25, abs=1e-3)


def test_an_undated_round_counts_half_and_a_future_one_in_full():
    assert score(round_node("r1", "startup", [trusted(lead=True)], None)) == 0.5
    assert score(round_node("r1", "startup", [trusted(lead=True)], "2027-01-01")) == 1.0


@pytest.mark.parametrize(
    ("rank", "weight"), [("FILING", 1.0), ("PRIMARY", 0.9), ("PRESS", 0.75), ("AGGREGATOR", 0.6)]
)
def test_a_weaker_source_counts_less(rank, weight):
    assert score(round_node("r1", "startup", [trusted(lead=True, rank=rank)])) == weight


def test_the_weakest_edge_of_the_path_sets_the_source_weight():
    own = round_node("r1", "startup", [trusted(lead=True)], issuer_rank="PRESS")
    assert score(own) == 0.75


def test_one_investor_away_counts_far_less_than_a_direct_backer():
    direct = score(round_node("r1", "startup", [trusted(lead=True)]))
    own = round_node("r1", "startup", [middle(lead=True)])
    other = round_node("r2", "other", [middle(), trusted()])
    candidate, graph = startup(own, others=[other])
    found = proximity(candidate, graph, [TRUSTED], today=TODAY)

    [path] = found.paths
    assert path.ring == 2
    # 0.3 for the distance, and Middle VC has 2 rounds in the graph: 1 / log2(2 + 2).
    assert path.strength == found.score == 0.15
    assert direct == 1.0
    assert path.explanation == (
        "Middle VC, who led Startup's Seed r1, invested alongside Trusted Fund in "
        "Other's Seed r2 (2026)."
    )
    assert [f.value for f in path.facts] == ["Startup · Seed r1", "Other · Seed r2"]
    assert all(f.sources for f in path.facts)


def test_a_hub_intermediary_counts_less_than_a_selective_one():
    own = round_node("r1", "startup", [middle(lead=True)])
    shared = round_node("r2", "other", [middle(), trusted()])
    busy = [round_node(f"x{n}", f"co{n}", [middle()]) for n in range(14)]
    selective = score(own, others=[shared])
    hub = score(own, others=[shared, *busy])
    assert selective == 0.15
    assert hub == round(0.3 / math.log2(2 + 16), 4)
    assert hub < selective


def test_ring_two_takes_the_intermediary_role_the_oldest_round_and_the_weakest_edge():
    shared = round_node("r2", "other", [middle(), trusted(lead=True)])
    joined = score(round_node("r1", "startup", [middle()]), others=[shared])
    assert joined == round(0.3 * 0.6 * 0.5, 4)

    own = round_node("r1", "startup", [middle(lead=True)])
    old = round_node("r2", "other", [middle(), trusted()], THREE_YEARS_AGO)
    assert score(own, others=[old]) == round(0.3 * 0.5 * 0.5, 4)

    press = round_node("r2", "other", [middle(), trusted(rank="PRESS")])
    assert score(own, others=[press]) == round(0.3 * 0.75 * 0.5, 4)


def test_a_trusted_investor_is_never_its_own_intermediary():
    own = round_node("r1", "startup", [trusted(lead=True)])
    other = round_node("r2", "other", [trusted(), party("t2", "Second Trusted")])
    second = ReferenceInvestor(entity_id="t2", name="Second Trusted")
    candidate, graph = startup(own, others=[other])
    found = proximity(candidate, graph, [TRUSTED, second], today=TODAY)
    assert [p.ring for p in found.paths] == [1]


def test_paths_add_up_strongest_first_with_their_sources():
    led = round_node("r1", "startup", [trusted(lead=True), middle()])
    joined = round_node("r0", "startup", [trusted()], THREE_YEARS_AGO)
    other = round_node("r2", "other", [middle(), trusted()])
    candidate, graph = startup(led, joined, others=[other])
    found = proximity(candidate, graph, [TRUSTED], today=TODAY)

    assert [(p.ring, p.strength) for p in found.paths] == [(1, 1.0), (1, 0.3), (2, 0.09)]
    assert found.score == 1.39
    assert found.paths[0].explanation == "Trusted Fund led Startup's Seed r1 (2026)."
    assert found.paths[1].explanation == "Trusted Fund joined Startup's Seed r0 (2023)."
    fact = found.paths[0].facts[0]
    assert fact.trust == "filing"
    assert {s.url for s in fact.sources} == {"https://t.example", "https://startup.example"}


def test_only_the_strongest_paths_are_kept_and_the_score_is_their_sum():
    own = [
        round_node(f"r{n}", "startup", [trusted(lead=n == 0)], f"{2026 - n}-01-01")
        for n in range(MAX_PATHS + 2)
    ]
    candidate, graph = startup(*own)
    found = proximity(candidate, graph, [TRUSTED], today=TODAY)
    strengths = [p.strength for p in found.paths]
    assert len(strengths) == MAX_PATHS
    assert strengths == sorted(strengths, reverse=True)
    assert found.score == round(sum(strengths), 4)


def test_a_reference_typed_by_name_matches_a_fund_under_another_cala_entity():
    typed = ReferenceInvestor(entity_id="unresolved:trusted fund", name="Trusted Fund")
    vehicle = party("t-vehicle", "Trusted Fund (Nordic Vehicle II)", lead=True)
    assert score(round_node("r1", "startup", [vehicle]), reference=[typed]) == 1.0

    own = round_node("r1", "startup", [middle(lead=True)])
    other = round_node("r2", "other", [party("m-oy", "Middle VC Oy"), vehicle])
    assert score(own, others=[other], reference=[typed]) == 0.15


def test_recorded_lead_reaches_500_global_through_two_other_rounds():
    rounds = {
        r["id"]: r
        for r in (
            load_cala("real_round_grei_preseed"),
            load_cala("real_round_callsy"),
            load_cala("real_round_rebookify"),
        )
    }
    own = rounds["3dba66dc-5eec-5c0d-96cb-60e88365ef65"]
    grei = build_candidate(
        {"id": "0094ec10-bd61-4833-bf19-c2ab9d78312b", "name": "GREÏ"}, [build_round(own)]
    )
    typed = ReferenceInvestor(entity_id="unresolved:500 global", name="500 Global")
    found = proximity(grei, LinkGraph(rounds=rounds), [typed], today=TODAY)

    assert [p.ring for p in found.paths] == [2, 2]
    assert found.score == round(sum(p.strength for p in found.paths), 4) > 0
    text = " ".join(p.explanation for p in found.paths)
    assert "Callsy AI" in text and "Rebookify" in text and "500 Global" in text
    assert all(f.sources for p in found.paths for f in p.facts)


def test_a_candidate_without_raw_rounds_is_scored_from_its_round_dates():
    from app.agent.sources import fixture_candidates

    kiln = next(c for c in fixture_candidates() if c.name == "Kiln Analytics")
    north_pine = ReferenceInvestor(entity_id="inv-north-pine", name="North Pine")
    found = proximity(kiln, LinkGraph(), [north_pine], today=date(2024, 5, 1))
    [path] = found.paths
    assert path.ring == 1 and path.strength == 1.0
    assert path.facts == [kiln.rounds[0].date]

import asyncio

import pytest

from app.cala.client import CalaError
from app.discovery.build import build_candidate, build_round
from app.discovery.links import (
    LinkLimits,
    Trusted,
    attach_links,
    hidden_links,
    walk_investors,
)
from app.discovery.pipeline import INVESTOR_BODY, ROUND_BODY
from app.models import ReferenceInvestor
from tests.conftest import load_cala

GREI = "0094ec10-bd61-4833-bf19-c2ab9d78312b"
FIRSTPICK = "88b67750-caa3-40ca-bfde-8eb88aa48ae4"
GREI_ROUND = "3dba66dc-5eec-5c0d-96cb-60e88365ef65"
CALLSY_ROUND = "4edc832c-ca28-5c7c-871e-4be638e16f4e"
REBOOKIFY_ROUND = "ae44bd34-20a9-586d-8796-b12981dfcd8d"
FIVE_HUNDRED = ReferenceInvestor(entity_id="unresolved:500 global", name="500 Global")


class FakeCala:
    """Answers from recorded nodes; unknown ids are a 404 like Cala's."""

    def __init__(self, nodes, delay=0.0):
        self.nodes = nodes
        self.delay = delay
        self.calls_made = 0
        self.asked: list[str] = []

    async def retrieve(self, entity_id, body=None, fresh=False):
        self.calls_made += 1
        self.asked.append(entity_id)
        if self.delay:
            await asyncio.sleep(self.delay)
        if entity_id not in self.nodes:
            raise CalaError(404, "not found")
        return self.nodes[entity_id]


def recorded():
    firstpick = load_cala("real_investor_firstpick")
    rounds = {
        r["id"]: r
        for r in (
            load_cala("real_round_grei_preseed"),
            load_cala("real_round_callsy"),
            load_cala("real_round_rebookify"),
        )
    }
    return firstpick, rounds


def grei(rounds):
    company = {"id": GREI, "name": "GREÏ", "properties": {}}
    return build_candidate(company, [build_round(rounds[GREI_ROUND])])


async def walk(candidates, nodes, raw, **limits):
    return await walk_investors(
        FakeCala(nodes), candidates, raw, LinkLimits(**limits), INVESTOR_BODY, ROUND_BODY
    )


async def test_recorded_lead_co_invested_with_a_trusted_fund_under_two_cala_entities():
    firstpick, rounds = recorded()
    assert firstpick["id"] == FIRSTPICK
    candidate = grei(rounds)
    raw = {GREI_ROUND: rounds[GREI_ROUND]}
    graph = await walk([candidate], {FIRSTPICK: firstpick, **rounds}, raw)

    [link] = hidden_links(candidate, graph, [FIVE_HUNDRED], [candidate])
    assert link.kind == "trusted_co_investor"
    assert link.count == 2
    assert link.label == "co-invested 2× with 500 Global"
    assert link.via_entity_id == FIRSTPICK
    assert "Callsy AI" in link.explanation and "Rebookify" in link.explanation
    ids = {n.entity_id for n in link.nodes}
    # Startup, its round, the lead, both proving rounds, their issuers and both 500 Global
    # entities ("500 Global" and "500 Global (500 Emerging Europe)").
    assert {GREI, GREI_ROUND, FIRSTPICK, CALLSY_ROUND, REBOOKIFY_ROUND} <= ids
    trusted_names = {n.name for n in link.nodes if n.name.startswith("500 Global")}
    assert trusted_names == {"500 Global", "500 Global (500 Emerging Europe)"}
    assert all(e.relationship == "PARTICIPATES_IN_FUNDING_ROUND" for e in link.edges)
    assert {e.role for e in link.edges} >= {"ISSUER", "is_lead", "GRANTOR", "INVESTOR"}
    assert all(e.source in ids and e.target in ids for e in link.edges)
    assert len(link.facts) == 2 and all(f.sources for f in link.facts)
    assert link.trust in ("press", "aggregator")


async def test_no_co_investor_link_without_trusted_investors_or_through_a_trusted_one():
    firstpick, rounds = recorded()
    candidate = grei(rounds)
    graph = await walk([candidate], {FIRSTPICK: firstpick, **rounds}, {})
    assert hidden_links(candidate, graph, [], [candidate]) == []
    # FIRSTPICK trusted itself is the direct co-invest signal, not a hidden link.
    trusted_lead = ReferenceInvestor(entity_id=FIRSTPICK, name="FIRSTPICK")
    assert hidden_links(candidate, graph, [trusted_lead], [candidate]) == []


def investor(iid, name, lead=False):
    return {
        "id": iid,
        "name": name,
        "entity_type": "Organization",
        "properties": {
            "role": "INVESTOR",
            "is_lead": lead,
            "sources": [{"name": "Press", "document": "https://p.example", "source_rank": "PRESS"}],
        },
    }


def round_node(rid, issuer, issuer_name, date, investors):
    issuer_edge = {
        "id": issuer,
        "name": issuer_name,
        "entity_type": "Company",
        "properties": {"role": "ISSUER", "sources": []},
    }
    return {
        "id": rid,
        "name": "Seed",
        "entity_type": "FundingRound",
        "properties": {"name": {"value": "Seed", "sources": []}, "event_date": {"value": date}},
        "relationships": {"incoming": {"PARTICIPATES_IN_FUNDING_ROUND": [issuer_edge, *investors]}},
    }


async def test_two_startups_on_the_list_sharing_a_fund_under_different_entities():
    ra = round_node("ra", "a", "Alpha AI", "2026-01-01", [investor("nv1", "North VC", True)])
    rb = round_node("rb", "b", "Beta AI Oy", "2025-06-01", [investor("nv2", "North VC Ltd")])
    rc = round_node("rc", "c", "Gamma", "2025-06-01", [investor("other", "Other")])
    alpha = build_candidate({"id": "a", "name": "Alpha AI"}, [build_round(ra)])
    beta = build_candidate({"id": "b", "name": "Beta AI Oy"}, [build_round(rb)])
    gamma = build_candidate({"id": "c", "name": "Gamma"}, [build_round(rc)])
    raw = {"ra": ra, "rb": rb, "rc": rc}
    graph = await walk([alpha, beta, gamma], {}, raw)

    linked = attach_links([alpha, beta, gamma], graph, [])
    [link] = linked[0].links
    assert link.kind == "shared_investor"
    assert link.label == "also backs Beta AI Oy"
    assert link.target.entity_id == "b"
    assert {n.entity_id for n in link.nodes} == {"a", "ra", "nv1", "nv2", "rb", "b"}
    assert link.trust == "aggregator"  # the issuer edges carry no source
    assert linked[1].links[0].target.entity_id == "a"
    assert linked[2].links == []


async def test_walk_stops_at_the_call_budget():
    firstpick, rounds = recorded()
    fake = FakeCala({FIRSTPICK: firstpick, **rounds})
    await walk_investors(
        fake, [grei(rounds)], {}, LinkLimits(call_budget=2), INVESTOR_BODY, ROUND_BODY
    )
    assert fake.calls_made == 2


async def test_a_slow_hub_node_is_skipped_not_fatal():
    firstpick, rounds = recorded()
    fake = FakeCala({FIRSTPICK: firstpick}, delay=0.05)
    graph = await walk_investors(
        fake, [grei(rounds)], {}, LinkLimits(timeout=0.01), INVESTOR_BODY, ROUND_BODY
    )
    assert graph.investors == {}
    assert fake.asked == [FIRSTPICK]


async def test_walk_reads_cached_nodes_from_raw_without_calling():
    firstpick, rounds = recorded()
    fake = FakeCala({})
    raw = {FIRSTPICK: firstpick, **rounds}
    graph = await walk_investors(fake, [grei(rounds)], raw, LinkLimits(), INVESTOR_BODY, ROUND_BODY)
    assert not set(fake.asked) & set(raw)  # the other five rounds are not recorded
    assert set(graph.investors[FIRSTPICK].round_ids) >= {CALLSY_ROUND, REBOOKIFY_ROUND}


@pytest.mark.parametrize(
    ("name", "matches"),
    [
        ("500 Global", True),
        ("500 Global (500 Emerging Europe)", True),
        ("500 Startups", False),
        ("Y Combinator Continuity", True),
        ("Combinator", False),
    ],
)
def test_trusted_matches_one_fund_under_several_names(name, matches):
    refs = [
        FIVE_HUNDRED,
        ReferenceInvestor(entity_id="yc", name="Y Combinator"),
    ]
    assert (Trusted(refs).match("some-id", name) is not None) is matches

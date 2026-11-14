"""Reverse walk (#191): trusted investors -> their rounds -> issuers attending the event."""

import asyncio
from datetime import UTC, date, datetime

import pytest

from app.agent import sources
from app.cala.client import CalaError
from app.discovery.links import InvestorRounds, LinkGraph
from app.discovery.pipeline import SLUSH_2026, DiscoveryResult, DiscoveryStats
from app.discovery.reverse import (
    ReverseLimits,
    ReverseResult,
    merge_candidates,
    merge_graphs,
    reverse_walk,
)
from app.models import ReferenceInvestor
from app.store import profile as profile_store
from tests.test_discovery import FakeCala, company, round_node, stub

TODAY = date(2026, 11, 14)
EVENT = SLUSH_2026
PARTICIPATES = "PARTICIPATES_IN_FUNDING_ROUND"
YC = ReferenceInvestor(entity_id="unresolved:y combinator", name="Y Combinator")


class ReverseCala(FakeCala):
    """FakeCala plus name search, paged investor edges, a count of calls and slow nodes."""

    def __init__(self, nodes, hits=None, failing=(), slow=()):
        super().__init__(nodes, failing)
        self.hits = hits or {}
        self.slow = set(slow)
        self.calls_made = 0
        self.bodies: list[tuple[str, dict | None]] = []

    async def search(self, name, entity_types=None, limit=20):
        self.calls_made += 1
        self.calls.append(("search", name))
        if name in self.failing:
            raise CalaError(500, "boom")
        return self.hits.get(name, [])[:limit]

    async def introspect(self, entity_id):
        self.calls_made += 1
        return await super().introspect(entity_id)

    async def retrieve(self, entity_id, body=None, fresh=False):
        self.calls_made += 1
        self.bodies.append((entity_id, body))
        if entity_id in self.slow:
            await asyncio.sleep(0.2)
        if entity_id in self.failing:
            self.calls.append(("retrieve", entity_id))
            raise CalaError(500, "boom")
        node = await super().retrieve(entity_id, body, fresh)
        page = ((body or {}).get("relationships") or {}).get("outgoing", {}).get(PARTICIPATES)
        edges = ((node.get("relationships") or {}).get("outgoing") or {}).get(PARTICIPATES)
        if page is None or edges is None or "limit" not in page:
            return node
        start = page.get("offset", 0)
        sliced = edges[start : start + page["limit"]]
        return {**node, "relationships": {"outgoing": {PARTICIPATES: sliced}}}

    def asked(self, kind="retrieve"):
        return [entity_id for k, entity_id in self.calls if k == kind]


def fund(entity_id, name, rounds=(), etype="Organization", issued=()):
    edges = [
        {"id": r, "name": "Round", "entity_type": "FundingRound", "properties": {"role": role}}
        for role, ids in (("INVESTOR", rounds), ("ISSUER", issued))
        for r in ids
    ]
    return {
        "id": entity_id,
        "name": name,
        "entity_type": etype,
        "properties": {},
        "relationships": {"outgoing": {PARTICIPATES: edges}},
    }


def hit(node):
    return {"id": node["id"], "name": node["name"], "entity_type": node["entity_type"]}


def startup(cid, name, round_id):
    return company(cid, name, stage="SEED", founded="2024-01-01", rounds=[round_id])


@pytest.fixture
def world():
    """Y Combinator as three entities; Zeta and Yota attend and are startups, BigCo attends
    and is not, Elsewhere raised from YC and does not attend."""
    funds = [
        fund("yc-co", "Y Combinator", ["rz", "rx", "rb"], "Company", issued=["own-raise"]),
        fund("yc-org", "Y Combinator"),
        fund("yc-w24", "Y Combinator W24", ["ry", "rz"], "Group"),
    ]
    lookalike = fund("combinator-labs", "Combinator Labs", ["rl"])
    attendees = [
        stub("kide", "Kide Health"),
        stub("zeta", "Zeta"),
        stub("yota", "Yota"),
        stub("bigco", "BigCo"),
        stub("yc-co", "Y Combinator"),
    ]
    nodes = {
        EVENT: {
            "id": EVENT,
            "name": "Slush 2026",
            "entity_type": "Event",
            "relationships": {"incoming": {"PARTICIPATES_IN_EVENT": attendees}},
        },
        **{f["id"]: f for f in [*funds, lookalike]},
        "zeta": startup("zeta", "Zeta", "rz"),
        "yota": startup("yota", "Yota", "ry"),
        "bigco": company("bigco", "BigCo", founded="1990-01-01", size=[5000], rounds=["rb"]),
        "rz": round_node("rz", "zeta", "2026-05-01", [("yc-co", False), ("yc-w24", False)]),
        "ry": round_node("ry", "yota", "2026-06-01", [("yc-w24", False)]),
        "rb": round_node("rb", "bigco", "2020-01-01", [("yc-co", False)]),
        "rx": round_node("rx", "elsewhere", "2025-01-01", [("yc-co", False)]),
        "rl": round_node("rl", "zeta", "2025-01-01", [("combinator-labs", True)]),
    }
    hits = {"Y Combinator": [hit(f) for f in [funds[0], lookalike, funds[1], funds[2]]]}
    return nodes, hits


async def test_every_entity_of_the_fund_leads_to_the_attending_startups_it_funded(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert [c.name for c in result.candidates] == ["Zeta", "Yota"]
    zeta = result.candidates[0]
    assert zeta.rounds[0].entity_id == "rz"
    assert {s.kind for s in zeta.signals} >= {"co_invest", "lead_follow_on", "likely_to_raise"}
    s = result.stats
    assert (s.entities, s.rounds, s.issuers, s.attending, s.startups) == (3, 4, 4, 3, 2)
    assert s.skipped == 0 and s.budget_spent is False
    asked = cala.asked()
    assert "combinator-labs" not in asked and "rl" not in asked  # another fund's name
    assert "own-raise" not in asked  # a round the fund issued, not one it funded
    assert "elsewhere" not in asked  # issuer that does not attend
    assert all(asked.count(rid) == 1 for rid in ("rz", "ry", "rb", "rx"))


async def test_rounds_and_fund_entities_read_land_in_the_link_graph(world):
    nodes, hits = world
    result = await reverse_walk(ReverseCala(nodes, hits), [YC], EVENT, TODAY)

    graph = result.links
    assert set(graph.investors) == {"yc-co", "yc-org", "yc-w24"}
    assert graph.investors["yc-co"].round_ids == ["rz", "rx", "rb"]
    assert graph.investors["yc-org"].round_ids == []
    assert graph.investors["yc-w24"].entity_type == "Group"
    assert set(graph.rounds) == {"rz", "ry", "rb", "rx"}
    assert result.investors["y combinator"] in ("yc-co", "yc-org")
    assert result.investors["y combinator w24"] == "yc-w24"


async def test_investor_edges_are_read_page_by_page(world):
    nodes, hits = world
    rounds = [f"missing-{n}" for n in range(230)]
    rounds[215] = "ry"
    nodes["yc-co"] = fund("yc-co", "Y Combinator", rounds, "Company")
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    pages = [
        body["relationships"]["outgoing"][PARTICIPATES]
        for entity_id, body in cala.bodies
        if entity_id == "yc-co"
    ]
    assert pages == [{"limit": 100}, {"limit": 100, "offset": 100}, {"limit": 100, "offset": 200}]
    assert "Yota" in [c.name for c in result.candidates]
    assert result.links.investors["yc-co"].round_ids == ["ry"]  # the 229 others are 404s


async def test_a_resolved_reference_is_walked_even_when_search_fails(world):
    nodes, hits = world
    ref = ReferenceInvestor(entity_id="yc-w24", name="Y Combinator")
    cala = ReverseCala(nodes, hits, failing=["Y Combinator"])

    result = await reverse_walk(cala, [ref], EVENT, TODAY)

    assert set(result.links.investors) == {"yc-w24"}
    assert [c.name for c in result.candidates] == ["Yota", "Zeta"]


async def test_a_spent_budget_returns_what_was_read(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits)

    # Attendees, search, yc-co, rz, then Zeta's introspection and node: six new calls.
    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(call_budget=6))

    assert result.stats.budget_spent is True
    assert [c.name for c in result.candidates] == ["Zeta"]
    assert cala.calls_made == 6
    assert result.links.investors["yc-co"].round_ids == ["rz"]


async def test_cala_errors_skip_the_node_and_keep_the_rest(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits, failing=["rx", "zeta", "yc-org"])

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert [c.name for c in result.candidates] == ["Yota"]
    assert result.stats.skipped == 2  # the fund entity and the company; the round is not read
    assert "rx" not in result.links.rounds


async def test_without_the_attendee_list_there_is_nothing_to_cross(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits, failing=[EVENT])

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert result.candidates == [] and result.links.investors == {}
    assert cala.asked("search") == []


async def test_a_slow_node_times_out_and_is_skipped(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits, slow=["rz"])

    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(timeout=0.05))

    assert [c.name for c in result.candidates] == ["Yota"]


async def test_no_references_makes_no_cala_call(world):
    nodes, hits = world
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [], EVENT, TODAY)

    assert result.candidates == [] and cala.calls_made == 0


YC_CO = ("yc", "Y Combinator")
YC_W24 = ("yc-w24", "Y Combinator W24")
PIONEER_A = ("pioneer-a", "Pioneer Fund")
PIONEER_B = ("pioneer-b", "Pioneer Fund")
SV = ("sv", "SV Angel")
ADA = ("ada", "Ada Lovelace")
REBEL = ("rebel", "Rebel Fund")
ONCE = ("once", "Once Capital")


def shared_round(rid, issuer, funders):
    node = round_node(rid, issuer, "2025-01-01", [(fid, False) for fid, _ in funders])
    edges = node["relationships"]["incoming"][PARTICIPATES][1:]
    for edge, (_, name) in zip(edges, funders, strict=True):
        edge["name"] = name
    return node


@pytest.fixture
def rings():
    """Y Combinator funded five rounds. Next to it: Pioneer Fund in three (as two entities),
    SV Angel and the angel Ada Lovelace in two each, Rebel Fund and Once Capital in one.
    Zeta attends and raised from YC; Yota (Pioneer), Nova (SV) and Hidden (Rebel) attend too,
    and so does Zeta's legal entity, which raised from Pioneer."""
    attendees = [
        stub("zeta", "Zeta"),
        stub("zeta-oy", "Zeta"),
        stub("yota", "Yota"),
        stub("nova", "Nova"),
        stub("hidden", "Hidden"),
        stub("bigco", "BigCo"),
    ]
    yc = fund("yc", "Y Combinator", ["r1", "r2", "r3", "r4", "r5"], "Company")
    nodes = {
        EVENT: {
            "id": EVENT,
            "name": "Slush 2026",
            "entity_type": "Event",
            "relationships": {"incoming": {"PARTICIPATES_IN_EVENT": attendees}},
        },
        "yc": yc,
        "yc-w24": fund("yc-w24", "Y Combinator W24", ["r1", "r2", "w1"], "Group"),
        "pioneer-a": fund("pioneer-a", "Pioneer Fund", ["r1", "r2", "p1"]),
        "pioneer-b": fund("pioneer-b", "Pioneer Fund", ["r3", "p2"]),
        "sv": fund("sv", "SV Angel", ["r2", "r3", "s1"]),
        "ada": fund("ada", "Ada Lovelace", ["r4", "r5", "a1"], "Person"),
        "rebel": fund("rebel", "Rebel Fund", ["r4", "x1"]),
        "zeta": startup("zeta", "Zeta", "r1"),
        "zeta-oy": startup("zeta-oy", "Zeta", "p2"),
        "yota": startup("yota", "Yota", "p1"),
        "nova": startup("nova", "Nova", "s1"),
        "hidden": startup("hidden", "Hidden", "x1"),
        "bigco": company("bigco", "BigCo", founded="1990-01-01", size=[5000], rounds=["a1"]),
        "r1": shared_round("r1", "zeta", [YC_CO, YC_W24, PIONEER_A]),
        "r2": shared_round("r2", "e2", [YC_CO, YC_W24, PIONEER_A, SV]),
        "r3": shared_round("r3", "e3", [YC_CO, PIONEER_B, SV]),
        "r4": shared_round("r4", "e4", [YC_CO, ADA, REBEL]),
        "r5": shared_round("r5", "e5", [YC_CO, ADA, ONCE]),
        "p1": shared_round("p1", "yota", [PIONEER_A]),
        "p2": shared_round("p2", "zeta-oy", [PIONEER_B]),
        "s1": shared_round("s1", "nova", [SV]),
        "a1": shared_round("a1", "bigco", [ADA]),
        "x1": shared_round("x1", "hidden", [REBEL]),
    }
    return nodes, {"Y Combinator": [hit(yc)]}


async def test_co_investors_are_ranked_by_shared_rounds_and_merged_by_name(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert [(c.name, c.shared_rounds, c.trusted) for c in result.co_investors] == [
        ("Pioneer Fund", 3, "Y Combinator"),
        ("Ada Lovelace", 2, "Y Combinator"),
        ("SV Angel", 2, "Y Combinator"),
    ]
    assert result.co_investors[0].entity_ids == ["pioneer-a", "pioneer-b"]
    s = result.stats
    assert (s.co_investors, s.co_investors_walked, s.co_investors_skipped) == (5, 3, 0)
    asked = cala.asked()
    walked = [i for i in asked if i in ("yc", "pioneer-a", "pioneer-b", "sv", "ada")]
    assert walked == ["yc", "pioneer-a", "pioneer-b", "ada", "sv"]
    assert "yc-w24" not in asked and "w1" not in asked  # the trusted fund's own entity
    assert "rebel" not in asked and "once" not in asked  # one shared round only


async def test_second_ring_adds_the_attending_startups_its_co_investors_funded(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert [c.name for c in result.candidates] == ["Zeta", "Yota", "Nova"]
    s = result.stats
    assert (s.startups, s.second_ring_startups) == (3, 2)
    assert (s.rounds, s.issuers, s.attending) == (9, 9, 5)
    asked = cala.asked()
    assert "zeta-oy" not in asked  # Zeta is a ring 1 candidate already
    assert asked.count("zeta") == 1
    assert all(asked.count(rid) == 1 for rid in ("r1", "r2", "r3", "p1", "p2", "s1", "a1"))


async def test_second_ring_rounds_and_investors_join_the_link_graph(rings):
    nodes, hits = rings
    result = await reverse_walk(ReverseCala(nodes, hits), [YC], EVENT, TODAY)

    graph = result.links
    assert set(graph.investors) == {"yc", "pioneer-a", "pioneer-b", "sv", "ada"}
    assert graph.investors["pioneer-a"].round_ids == ["r1", "r2", "p1"]
    assert graph.investors["ada"].entity_type == "Person"
    assert {"p1", "p2", "s1", "a1"} <= set(graph.rounds)
    assert result.investors["pioneer fund"] == "pioneer-a"
    assert result.investors["sv angel"] == "sv"


async def test_at_most_k_co_investors_are_walked(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(co_investors=1))

    assert [c.name for c in result.co_investors] == ["Pioneer Fund"]
    assert [c.name for c in result.candidates] == ["Zeta", "Yota"]
    assert "sv" not in cala.asked() and "ada" not in cala.asked()
    assert result.stats.co_investors == 5 and result.stats.co_investors_walked == 1


async def test_co_investors_below_the_minimum_of_shared_rounds_are_not_walked(rings):
    nodes, hits = rings

    strict = await reverse_walk(
        ReverseCala(nodes, hits), [YC], EVENT, TODAY, ReverseLimits(min_shared_rounds=3)
    )
    loose = await reverse_walk(
        ReverseCala(nodes, hits), [YC], EVENT, TODAY, ReverseLimits(min_shared_rounds=1)
    )

    assert [c.name for c in strict.co_investors] == ["Pioneer Fund"]
    assert [c.name for c in strict.candidates] == ["Zeta", "Yota"]
    assert "Rebel Fund" in [c.name for c in loose.co_investors]
    assert "Hidden" in [c.name for c in loose.candidates]


def test_second_ring_defaults():
    limits = ReverseLimits()

    assert limits.second_ring is True
    assert (limits.co_investors, limits.min_shared_rounds, limits.hub_round_edges) == (10, 2, 300)


async def test_a_hub_co_investor_is_skipped_and_logged(rings, caplog):
    nodes, hits = rings
    nodes["sv"] = fund("sv", "SV Angel", ["r2", "r3", "s1", *(f"hub-{n}" for n in range(250))])
    cala = ReverseCala(nodes, hits)

    with caplog.at_level("WARNING", logger="app.discovery.reverse"):
        result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(hub_round_edges=150))

    pages = [
        body["relationships"]["outgoing"][PARTICIPATES]
        for entity_id, body in cala.bodies
        if entity_id == "sv"
    ]
    assert pages == [{"limit": 100}, {"limit": 100, "offset": 100}]  # stops past the cap
    assert "s1" not in cala.asked() and "hub-0" not in cala.asked()
    assert [c.name for c in result.candidates] == ["Zeta", "Yota"]
    assert "sv" not in result.links.investors
    s = result.stats
    assert (s.co_investors_walked, s.co_investors_skipped) == (2, 1)
    assert "hub co-investor SV Angel" in caplog.text


async def test_a_co_investor_under_the_hub_cap_is_walked_in_full(rings):
    nodes, hits = rings
    nodes["sv"] = fund("sv", "SV Angel", [*(f"missing-{n}" for n in range(120)), "s1"])
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY)

    assert "Nova" in [c.name for c in result.candidates]
    assert result.stats.co_investors_skipped == 0


async def test_a_budget_spent_in_the_second_ring_returns_what_was_read(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    # Ring 1 is ten new calls; then both Pioneer entities, p1, Yota's introspection and node.
    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(call_budget=15))

    assert cala.calls_made == 15
    assert result.stats.budget_spent is True
    assert [c.name for c in result.candidates] == ["Zeta", "Yota"]
    assert result.stats.second_ring_startups == 1
    assert result.stats.co_investors_walked == 1
    assert set(result.links.investors) == {"yc", "pioneer-a", "pioneer-b"}
    assert result.links.investors["pioneer-b"].round_ids == ["r3"]  # p2 was never read
    assert "sv" not in cala.asked() and "ada" not in cala.asked()


async def test_second_ring_never_starts_before_ring_one_is_done(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(call_budget=9))

    assert cala.calls_made == 9
    assert result.links.investors["yc"].round_ids == ["r1", "r2", "r3", "r4"]
    assert set(result.links.investors) == {"yc"}
    assert result.stats.co_investors_walked == 0


async def test_second_ring_can_be_turned_off(rings):
    nodes, hits = rings
    cala = ReverseCala(nodes, hits)

    result = await reverse_walk(cala, [YC], EVENT, TODAY, ReverseLimits(second_ring=False))

    assert [c.name for c in result.candidates] == ["Zeta"]
    assert result.co_investors == [] and result.stats.co_investors == 0
    assert set(result.links.investors) == {"yc"}
    assert "pioneer-a" not in cala.asked()


def test_merge_keeps_the_event_walk_and_drops_repeats_by_id_or_name():
    found = sources.fixture_candidates()
    same_id = found[0].model_copy(update={"name": "Another name"})
    same_name = found[1].model_copy(update={"entity_id": "legal-entity"})
    new = found[2].model_copy(update={"entity_id": "new", "name": "Brand New"})

    merged = merge_candidates(found, [same_id, same_name, new, new])

    assert merged[: len(found)] == found
    assert [c.entity_id for c in merged[len(found) :]] == ["new"]


def test_merged_graph_has_both_walks_and_leaves_them_untouched():
    base = LinkGraph(
        investors={"a": InvestorRounds("a", "A", "Company", ["r1"])}, rounds={"r1": {"id": "r1"}}
    )
    extra = LinkGraph(
        investors={
            "a": InvestorRounds("a", "A", "Company", ["r1", "r2"]),
            "b": InvestorRounds("b", "B", "Organization", ["r2"]),
        },
        rounds={"r2": {"id": "r2"}},
    )

    merged = merge_graphs(base, extra)

    assert merged.investors["a"].round_ids == ["r1", "r2"]
    assert set(merged.investors) == {"a", "b"} and set(merged.rounds) == {"r1", "r2"}
    assert base.investors["a"].round_ids == ["r1"] and set(base.rounds) == {"r1"}


def _discovery(monkeypatch, found, reverse: ReverseResult):
    """Both walks faked at the seam; returns the references each reverse walk was asked for."""
    asked: list[list[str]] = []

    async def event_walk(client, profile, today=None, limits=None, on_progress=None):
        return DiscoveryResult(candidates=found, stats=DiscoveryStats())

    async def fake_reverse_walk(client, references, event_id=None, today=None, limits=None):
        asked.append([r.name for r in references])
        return reverse

    monkeypatch.setattr(sources, "get_candidates", event_walk)
    monkeypatch.setattr(sources, "reverse_walk", fake_reverse_walk)
    return asked


def _trusting(*names):
    refs = [ReferenceInvestor(entity_id=f"unresolved:{n.lower()}", name=n) for n in names]
    return profile_store.current().model_copy(update={"reference_investors": refs})


async def test_candidates_are_the_union_of_both_walks_without_repeats(monkeypatch):
    found = sources.fixture_candidates()
    new = found[0].model_copy(update={"entity_id": "new", "name": "Brand New"})
    _discovery(monkeypatch, found[:2], ReverseResult(candidates=[found[1], new]))

    result = await sources.candidates_for(_trusting("Y Combinator"))

    assert [c.entity_id for c in result] == [found[0].entity_id, found[1].entity_id, "new"]


async def test_profile_filters_apply_to_the_reverse_walk_too(monkeypatch):
    found = sources.fixture_candidates()
    finn = next(c for c in found if "Finland" in str(c.hq.value))
    other = next(c for c in found if c.hq.value and "Finland" not in str(c.hq.value))
    _discovery(monkeypatch, [], ReverseResult(candidates=[finn, other]))
    profile = _trusting("Y Combinator")
    profile.filters.countries = ["Finland"]

    result = await sources.candidates_for(profile)

    assert [c.entity_id for c in result] == [finn.entity_id]


async def test_no_reference_investors_never_starts_the_reverse_walk(monkeypatch):
    found = sources.fixture_candidates()
    asked = _discovery(monkeypatch, found, ReverseResult(candidates=[]))

    result = await sources.candidates_for(_trusting())

    assert asked == []
    assert [c.entity_id for c in result] == [c.entity_id for c in found]


async def test_reverse_walk_is_cached_per_event_and_set_of_investors(monkeypatch):
    asked = _discovery(monkeypatch, [], ReverseResult())
    clock = {"now": datetime(2026, 11, 14, 12, tzinfo=UTC)}
    monkeypatch.setattr(sources, "_now", lambda: clock["now"])

    await sources.candidates_for(_trusting("Y Combinator", "500 Global"))
    await sources.candidates_for(_trusting("500 Global", "Y Combinator"))
    assert len(asked) == 1
    await sources.candidates_for(_trusting("Y Combinator"))
    assert len(asked) == 2
    other_event = _trusting("Y Combinator").model_copy(update={"event_id": "another-event"})
    await sources.candidates_for(other_event)
    assert len(asked) == 3
    clock["now"] += sources.DISCOVERY_TTL
    await sources.candidates_for(_trusting("Y Combinator"))
    assert len(asked) == 4


async def test_a_walk_cut_short_by_its_budget_is_walked_again_next_turn(monkeypatch):
    partial = ReverseResult()
    partial.stats.budget_spent = True
    asked = _discovery(monkeypatch, [], partial)

    await sources.candidates_for(_trusting("Y Combinator"))
    await sources.candidates_for(_trusting("Y Combinator"))
    assert len(asked) == 2

    partial.stats.budget_spent = False
    await sources.candidates_for(_trusting("Y Combinator"))
    await sources.candidates_for(_trusting("Y Combinator"))
    assert len(asked) == 3


async def test_hidden_links_see_the_rounds_the_reverse_walk_read(monkeypatch):
    found = sources.fixture_candidates()
    startup_ = next(c for c in found if c.rounds and c.rounds[0].investors)
    backer = startup_.rounds[0].investors[0]
    proof = round_node("proof", "elsewhere", "2025-01-01", [(backer.entity_id, True), ("yc", 0)])
    proof["relationships"]["incoming"][PARTICIPATES][2]["name"] = "Y Combinator"
    reverse = ReverseResult(
        links=LinkGraph(
            investors={"yc": InvestorRounds("yc", "Y Combinator", "Company", ["proof"])},
            rounds={"proof": proof},
        )
    )
    _discovery(monkeypatch, [startup_], reverse)

    [result] = await sources.candidates_for(_trusting("Y Combinator"))

    assert [(k.kind, k.target.name) for k in result.links] == [
        ("trusted_co_investor", "Y Combinator")
    ]

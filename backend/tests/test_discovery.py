from datetime import date

import pytest

from app.cala.client import CalaError
from app.discovery.build import build_round, normalise_name, participants
from app.discovery.filters import is_startup, matches_profile
from app.discovery.pipeline import SLUSH_2026, Limits, get_candidates, neutral_profile
from app.models import ProfileFilters, ReferenceInvestor
from tests.conftest import load_cala

TODAY = date(2026, 11, 14)


def make_profile(reference=(), **filters):
    base = {"stages": [], "sectors_in": [], "sectors_out": [], "countries": []}
    return neutral_profile().model_copy(
        update={
            "filters": ProfileFilters(**{**base, **filters}),
            "reference_investors": list(reference),
        }
    )


EVENT = SLUSH_2026
NORTHWIND = "c0000000-0000-4000-8000-000000000001"
AURORA = "v0000000-0000-4000-8000-000000000001"


def prop(value, rank="PRIMARY"):
    return {
        "value": value,
        "sources": [{"name": "s", "document": "https://s.example", "source_rank": rank}],
    }


def company(cid, name, *, stage=None, founded=None, size=None, hq=None, rounds=(), etype="Company"):
    props = {"name": prop(name)}
    if stage:
        props["funding_stage"] = prop(stage, "PRESS")
    if founded:
        props["founding_date"] = prop(founded, "FILING")
    if size:
        props["employee_count_range"] = prop(size, "AGGREGATOR")
    if hq:
        props["headquarters_address"] = prop(hq, "FILING")
    edges = [
        {
            "id": rid,
            "name": "Round",
            "entity_type": "FundingRound",
            "properties": {"role": "ISSUER"},
        }
        for rid in rounds
    ]
    return {
        "id": cid,
        "name": name,
        "entity_type": etype,
        "properties": props,
        "relationships": {"outgoing": {"PARTICIPATES_IN_FUNDING_ROUND": edges}, "incoming": {}},
        "numerical_observations": [],
    }


def round_node(rid, issuer, when, investors):
    edges = [
        {"id": issuer, "name": issuer, "entity_type": "Company", "properties": {"role": "ISSUER"}}
    ]
    edges += [
        {
            "id": iid,
            "name": iid,
            "entity_type": "Organization",
            "properties": {"role": "INVESTOR", "is_lead": lead},
        }
        for iid, lead in investors
    ]
    return {
        "id": rid,
        "name": "Seed",
        "entity_type": "FundingRound",
        "properties": {"name": prop("Seed"), "event_date": prop(when, "PRESS")},
        "relationships": {"incoming": {"PARTICIPATES_IN_FUNDING_ROUND": edges}, "outgoing": {}},
    }


def stub(cid, name, etype="Company"):
    return {"id": cid, "name": name, "entity_type": etype, "properties": {"role": "ATTENDEE"}}


class FakeCala:
    """Answers from a dict of nodes; pages the event like Cala does."""

    def __init__(self, nodes, failing=()):
        self.nodes = nodes
        self.failing = set(failing)
        self.calls: list[tuple[str, str]] = []

    async def introspect(self, entity_id):
        self.calls.append(("introspect", entity_id))
        if entity_id in self.failing:
            raise CalaError(500, "boom")
        node = self.nodes[entity_id]
        rels = node.get("relationships") or {}
        return {
            "properties": list((node.get("properties") or {}).keys()),
            "relationships": {
                d: list((rels.get(d) or {}).keys()) for d in ("incoming", "outgoing")
            },
            "numerical_observations": {
                "ObservableProperty": [
                    {"id": s["id"], "name": s["name"]}
                    for s in node.get("numerical_observations") or []
                ]
            },
        }

    async def retrieve(self, entity_id, body=None, fresh=False):
        self.calls.append(("retrieve", entity_id))
        node = self.nodes[entity_id]
        page = (
            ((body or {}).get("relationships") or {})
            .get("incoming", {})
            .get("PARTICIPATES_IN_EVENT")
        )
        if page is None:
            return node
        attendees = node["relationships"]["incoming"]["PARTICIPATES_IN_EVENT"]
        sliced = attendees[page["offset"] : page["offset"] + page["limit"]]
        return {**node, "relationships": {"incoming": {"PARTICIPATES_IN_EVENT": sliced}}}


@pytest.fixture
def graph():
    northwind = load_cala("company_startup")
    attendees = [
        stub(NORTHWIND, "Northwind Robotics Oy"),
        stub("dup", "Northwind Robotics"),  # same company under its brand: deduplicated
        stub(AURORA, "Aurora Ventures", "Organization"),  # a fund, not a candidate
        stub("oldcorp", "OldCorp"),
        stub("kide", "Kide Health"),
    ]
    aurora_rounds = ["ra", "rb", "rc", "rd", "r0000000-0000-4000-8000-000000000001"]
    nodes = {
        EVENT: {
            "id": EVENT,
            "name": "Slush 2026",
            "entity_type": "Event",
            "relationships": {"incoming": {"PARTICIPATES_IN_EVENT": attendees}},
        },
        NORTHWIND: northwind,
        "r0000000-0000-4000-8000-000000000001": load_cala("round_seed"),
        "oldcorp": company("oldcorp", "OldCorp", founded="1990-01-01", size=[5000]),
        "kide": company("kide", "Kide Health", stage="SERIES_A", hq="Tallinn, EE", rounds=["rk"]),
        "rk": round_node("rk", "kide", "2026-03-01", [("other-vc", True)]),
        "other-vc": {"id": "other-vc", "name": "Other VC", "entity_type": "Organization"},
        AURORA: {
            "id": AURORA,
            "name": "Aurora Ventures",
            "entity_type": "Organization",
            "properties": {},
            "relationships": {
                "outgoing": {
                    "PARTICIPATES_IN_FUNDING_ROUND": [
                        {
                            "id": r,
                            "name": "Round",
                            "entity_type": "FundingRound",
                            "properties": {"role": "INVESTOR"},
                        }
                        for r in aurora_rounds
                    ]
                }
            },
        },
        "ra": round_node("ra", "alpha", "2022-01-01", [(AURORA, True)]),
        "rb": round_node("rb", "alpha", "2023-06-01", [(AURORA, False)]),
        "rc": round_node("rc", "beta", "2022-05-01", [(AURORA, True)]),
        "rd": round_node("rd", "gamma", "2023-02-01", [(AURORA, True)]),
    }
    return nodes


async def test_pipeline_keeps_startups_with_rounds_and_signals(graph):
    profile = make_profile([ReferenceInvestor(entity_id=AURORA, name="Aurora Ventures")])
    result = await get_candidates(FakeCala(graph), profile, TODAY, Limits(page_size=2))
    names = [c.name for c in result.candidates]
    assert names == ["Northwind Robotics", "Kide Health"]
    s = result.stats
    assert (s.attendees, s.companies, s.startups, s.candidates, s.skipped) == (5, 3, 2, 2, 0)

    northwind = result.candidates[0]
    assert northwind.rounds[0].investors[0].name == "Aurora Ventures"
    assert northwind.headcount.value == 18
    signals = {sig.kind: sig for sig in northwind.signals}
    assert signals["co_invest"].value == ["Aurora Ventures"]
    assert signals["lead_follow_on"].value == 0.33  # followed on in alpha, not beta or gamma
    assert signals["likely_to_raise"].value is True


async def test_profile_filters_apply(graph):
    profile = make_profile(countries=["EE"])
    result = await get_candidates(FakeCala(graph), profile, TODAY)
    # Northwind is in FI and is dropped; Kide passes.
    assert [c.name for c in result.candidates] == ["Kide Health"]
    # Investors of dropped startups are still known, so reference investors can resolve.
    assert result.investors["aurora ventures"] == AURORA


async def test_a_failing_attendee_is_skipped_not_fatal(graph):
    result = await get_candidates(FakeCala(graph, failing={"kide"}), make_profile(), TODAY)
    assert [c.name for c in result.candidates] == ["Northwind Robotics"]
    assert result.stats.skipped == 1


async def test_max_attendees_caps_the_walk(graph):
    fake = FakeCala(graph)
    await get_candidates(fake, make_profile(), TODAY, Limits(max_attendees=1))
    assert ("retrieve", "kide") not in fake.calls  # max_attendees respected


def test_is_startup_rules():
    assert is_startup(company("a", "A", stage="SEED"), TODAY)
    assert not is_startup(company("b", "B"), TODAY)  # no stage, no rounds
    assert not is_startup(company("c", "C", stage="SEED", etype="Organization"), TODAY)
    assert not is_startup(company("d", "D", stage="SEED", founded="2001-01-01"), TODAY)
    assert not is_startup(company("e", "E", stage="SEED", size=[51, 1000]), TODAY)


def test_participants_dedupe_and_exclude_issuer():
    node = round_node("r", "issuer", "2024-01-01", [("x", False), ("x2", True)])
    node["relationships"]["incoming"]["PARTICIPATES_IN_FUNDING_ROUND"][1]["name"] = "Fund Ltd"
    node["relationships"]["incoming"]["PARTICIPATES_IN_FUNDING_ROUND"][2]["name"] = "Fund"
    investors = participants(node)
    assert len(investors) == 1
    assert investors[0].is_lead is True


def test_lenders_are_marked_and_round_amount_has_units():
    built = build_round(load_cala("round_seed"))
    assert [(i.name, i.role, i.is_lead) for i in built.investors] == [
        ("Aurora Ventures", "investor", True),
        ("Baltic Angels", "investor", False),
        ("Nordic Growth Debt", "lender", False),
    ]
    assert (built.amount.value, built.amount.unit, built.amount.trust) == (
        3000000,
        "EUR",
        "primary",
    )
    assert built.date.sources[0].date_precision == "month"


def test_normalise_name_strips_legal_suffixes():
    assert normalise_name("Northwind Robotics Oy") == normalise_name("northwind robotics")


def test_matches_profile_lets_unpublished_fields_pass(graph):
    from app.discovery.build import build_candidate

    bare = build_candidate(company("z", "Z", stage="SEED"), [])
    assert matches_profile(bare, make_profile(countries=["FI"], sectors_in=["AI"]))
    assert not matches_profile(bare, make_profile(stages=["SERIES_A"]))


def test_warm_dump_writes_one_file_per_node(tmp_path):
    from scripts.warm import dump_raw

    assert dump_raw({"a": {"id": "a"}, "b": {"id": "b"}}, tmp_path / "out") == 2
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["a.json", "b.json"]

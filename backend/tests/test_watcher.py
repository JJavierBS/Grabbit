import copy
import sqlite3
from datetime import UTC, datetime

import pytest

from app.models import Profile, ReferenceInvestor
from app.scheduler import GrabbitScheduler, digest_trigger
from app.store.snapshots import WatchStore
from app.watcher.importance import passes, rule_score, score
from app.watcher.run import Watcher, merge
from app.watcher.snapshot import Change, diff
from tests.conftest import load_cala

NORTHWIND = "c0000000-0000-4000-8000-000000000001"
SEED = "r0000000-0000-4000-8000-000000000001"
AURORA = "v0000000-0000-4000-8000-000000000001"
NOW = datetime(2026, 11, 14, 12, 0, tzinfo=UTC)


class FakeCala:
    """Serves the startup and its seed round; `company` can be swapped to simulate time."""

    def __init__(self):
        self.company = load_cala("company_startup")
        self.round = load_cala("round_seed")
        self.fresh_reads = 0

    async def introspect(self, entity_id):
        node = self.company
        rels = node["relationships"]
        return {
            "properties": list(node["properties"]),
            "relationships": {d: list(rels[d]) for d in ("incoming", "outgoing")},
            "numerical_observations": {
                "ObservableProperty": [{"id": "m-employees", "name": "Number of employees"}]
            },
        }

    async def retrieve(self, entity_id, body=None, fresh=False):
        if entity_id == NORTHWIND:
            self.fresh_reads += fresh
            return copy.deepcopy(self.company)
        if entity_id == SEED:
            return copy.deepcopy(self.round)
        raise KeyError(entity_id)


class Bus:
    def __init__(self):
        self.events = []

    async def __call__(self, kind, payload):
        self.events.append((kind, payload))


@pytest.fixture
def setup():
    cala, bus = FakeCala(), Bus()
    store = WatchStore(sqlite3.connect(":memory:"))
    watcher = Watcher(cala, store, publish=bus, clock=lambda: NOW)
    profile = Profile(
        reference_investors=[ReferenceInvestor(entity_id=AURORA, name="Aurora Ventures")]
    )
    return cala, bus, store, watcher, profile


def snap(**overrides):
    base = {
        "name": "Northwind",
        "rounds": {},
        "executives": {},
        "headcount": 10,
        "status": "ACTIVE",
        "domains": {"northwind.example": "ACTIVE"},
        "acquisitions": {},
    }
    return {**base, **overrides}


# diff, one test per alert kind


def test_diff_new_round_names_its_lead():
    new = snap(
        rounds={
            "r1": {"name": "Series A", "date": "2026-11-01", "leads": ["Aurora"], "lead_ids": ["a"]}
        }
    )
    [change] = diff(snap(), new)
    assert (change.kind, change.key) == ("new_round", "r1")
    assert "led by Aurora" in change.title


def test_diff_executive_joined_and_left():
    joined = snap(executives={"IS_CTO_OF:p9": {"role": "CTO", "name": "Ada", "valid_until": None}})
    [change] = diff(snap(), joined)
    assert change.kind == "executive_change" and not change.data["left"]
    left = snap(
        executives={"IS_CTO_OF:p9": {"role": "CTO", "name": "Ada", "valid_until": "2026-11-01"}}
    )
    [change] = diff(joined, left)
    assert change.data == {"role": "CTO", "left": True}


def test_diff_headcount_jump_only_at_20_percent():
    assert diff(snap(headcount=10), snap(headcount=11)) == []
    [change] = diff(snap(headcount=10), snap(headcount=12))
    assert change.kind == "headcount_jump"


def test_diff_acquisition_and_status_and_domain():
    acq = snap(
        acquisitions={"e1": {"name": "MNA_COMPLETED", "role": "ACQUIRER", "date": "2026-11-01"}}
    )
    assert [c.kind for c in diff(snap(), acq)] == ["acquisition"]
    assert [c.kind for c in diff(snap(), snap(status="INACTIVE"))] == ["status_change"]
    dead = snap(domains={"northwind.example": "INACTIVE"})
    assert [c.key for c in diff(snap(), dead)] == ["domain:northwind.example"]


def test_diff_no_change_no_alert():
    assert diff(snap(), snap()) == []


# importance


def test_round_led_by_reference_investor_is_decisive():
    profile = Profile(reference_investors=[ReferenceInvestor(entity_id="a", name="Aurora")])
    change = Change("new_round", "r1", "t", "w", {"lead_ids": ["a"]})
    value, reason = rule_score(change, profile)
    assert value == 0.95 and "Aurora" in reason


async def test_llm_scorer_used_only_when_rules_are_not_decisive():
    calls = []

    async def scorer(change, profile):
        calls.append(change.kind)
        return 0.2, "minor"

    profile = Profile()
    assert await score(Change("headcount_jump", "k", "t", "w"), profile, scorer) == (0.2, "minor")
    ceo = Change("executive_change", "k", "t", "w", {"role": "CEO", "left": True})
    assert (await score(ceo, profile, scorer))[0] == 0.85
    assert calls == ["headcount_jump"]


def test_thresholds():
    assert passes(0.5, Profile(alert_threshold="medium"))
    assert not passes(0.5, Profile(alert_threshold="high"))
    assert passes(0.3, Profile(alert_threshold="low"))


# watcher end to end


async def test_first_run_is_a_baseline_without_alerts(setup):
    cala, bus, store, watcher, profile = setup
    assert await watcher.run_once(profile, [NORTHWIND]) == []
    assert store.snapshot(NORTHWIND)["rounds"]
    assert cala.fresh_reads == 1
    assert bus.events == []


async def test_real_change_is_scored_stored_published_and_deduped(setup):
    cala, bus, store, watcher, profile = setup
    await watcher.run_once(profile, [NORTHWIND])
    ceo = cala.company["relationships"]["incoming"]["IS_CEO_OF"][0]
    ceo["properties"]["valid_until"] = "2026-11-13"
    [alert] = await watcher.run_once(profile, [NORTHWIND])
    assert (alert.kind, alert.simulated, alert.importance) == ("executive_change", False, 0.85)
    assert alert.facts[0].value == "2026-11-13"
    assert bus.events[0][0] == "alert" and bus.events[0][1]["id"] == alert.id
    assert await watcher.run_once(profile, [NORTHWIND]) == []  # same change: no repeat
    assert len(store.alerts()) == 1


async def test_daily_cap_on_real_alerts(setup):
    cala, bus, store, watcher, profile = setup
    watcher.max_alerts_per_day = 0
    await watcher.run_once(profile, [NORTHWIND])
    cala.company["properties"]["operational_status"]["value"] = "INACTIVE"
    assert await watcher.run_once(profile, [NORTHWIND]) == []


async def test_simulated_round_goes_through_the_real_path_without_touching_state(setup):
    cala, bus, store, watcher, profile = setup
    await watcher.run_once(profile, [NORTHWIND])
    before = store.snapshot(NORTHWIND)
    [alert] = await watcher.simulate("example_new_round", profile)
    assert alert.simulated is True
    assert alert.kind == "new_round"
    assert alert.importance == 0.95  # led by Aurora, a reference investor
    assert alert.facts[0].value == 12000000
    assert store.snapshot(NORTHWIND) == before  # staged data never saved
    assert bus.events[-1][1]["simulated"] is True


async def test_simulate_without_prior_snapshot_makes_a_baseline_first(setup):
    cala, bus, store, watcher, profile = setup
    [alert] = await watcher.simulate("example_ceo_leaves", profile)
    assert alert.kind == "executive_change" and alert.simulated
    assert store.snapshot(NORTHWIND) is not None


def test_merge_appends_lists_and_merges_dicts():
    assert merge({"a": [1], "b": {"c": 1}}, {"a": [2], "b": {"d": 2}}) == {
        "a": [1, 2],
        "b": {"c": 1, "d": 2},
    }


# scheduler


def test_digest_trigger_by_cadence():
    assert "day_of_week='mon'" in str(digest_trigger(Profile(cadence="weekly")))
    assert "day_of_week" not in str(digest_trigger(Profile(cadence="event")))


async def test_scheduler_loads_both_jobs_and_replaces_them():
    async def job():
        return None

    sched = GrabbitScheduler(job, job)
    sched.apply(Profile(cadence="event"))
    sched.apply(Profile(cadence="weekly"))
    jobs = {j.id: j for j in sched.scheduler.get_jobs()}
    assert set(jobs) == {"watcher", "digest"}
    assert "mon" in str(jobs["digest"].trigger)
    assert jobs["watcher"].max_instances == 1

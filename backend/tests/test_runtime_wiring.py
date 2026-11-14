"""The seams that join Team 2's discovery and watcher with Team 3's agent and reports."""

from datetime import date

import pytest

from app import fixtures, runtime
from app.agent import sources
from app.cala.client import CalaCacheMiss
from app.discovery.pipeline import DiscoveryResult, DiscoveryStats
from app.store import profile as profile_store
from app.store import reports as report_store
from app.store.db import init_db
from app.watcher import run as watcher_run


@pytest.fixture(autouse=True)
def tables() -> None:
    init_db()


async def test_candidates_come_from_the_discovery_pipeline(monkeypatch):
    found = fixtures.latest_report().candidates[:1]
    seen = {}

    async def fake_get_candidates(client, profile, today: date | None = None, limits=None):
        seen["limit"] = limits.max_attendees
        return DiscoveryResult(candidates=found, stats=DiscoveryStats())

    monkeypatch.setattr(sources, "get_candidates", fake_get_candidates)

    result = await sources.candidates_for(profile_store.current())

    assert result == found
    assert seen["limit"] == sources.MAX_ATTENDEES


async def test_an_empty_shortlist_stays_empty(monkeypatch):
    async def nothing(client, profile, today=None, limits=None):
        return DiscoveryResult(candidates=[], stats=DiscoveryStats())

    monkeypatch.setattr(sources, "get_candidates", nothing)

    assert await sources.candidates_for(profile_store.current()) == []


async def test_cold_replay_cache_falls_back_to_fixture_candidates():
    result = await sources.candidates_for(profile_store.current())

    assert [c.entity_id for c in result] == [c.entity_id for c in sources.fixture_candidates()]


def test_lifespan_schedules_watcher_and_digest(client):
    scheduler = client.app.state.scheduler

    assert scheduler.running
    assert {job.id for job in scheduler.get_jobs()} == {"watcher", "digest"}


async def test_watcher_job_needs_a_report_first(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("no Cala call without a shortlist")

    monkeypatch.setattr(watcher_run, "Watcher", fail)

    await runtime.watcher_job()


async def test_watcher_job_checks_the_latest_report_shortlist(monkeypatch):
    report = fixtures.latest_report()
    report_store.add(report)
    calls = []

    class FakeWatcher:
        def __init__(self, client, store, publish):
            pass

        async def run_once(self, profile, shortlist):
            calls.append((profile.version, shortlist))
            return []

    monkeypatch.setattr(watcher_run, "Watcher", FakeWatcher)

    await runtime.watcher_job()

    assert calls == [(profile_store.current().version, [c.entity_id for c in report.candidates])]


async def test_watcher_keeps_watching_after_a_digest_with_nothing_new(monkeypatch):
    prep = fixtures.latest_report().model_copy(update={"id": "rep-prep", "kind": "prep"})
    quiet = prep.model_copy(update={"id": "rep-quiet", "kind": "digest", "candidates": []})
    report_store.add(prep)
    report_store.add(quiet)
    calls = []

    class FakeWatcher:
        def __init__(self, client, store, publish):
            pass

        async def run_once(self, profile, shortlist):
            calls.append(shortlist)
            return []

    monkeypatch.setattr(watcher_run, "Watcher", FakeWatcher)

    await runtime.watcher_job()

    assert calls == [[c.entity_id for c in prep.candidates]]


async def test_watcher_shortlist_adds_startups_from_digests_after_the_prep(monkeypatch):
    prep = fixtures.latest_report().model_copy(update={"id": "rep-prep", "kind": "prep"})
    first, *rest = prep.candidates
    report_store.add(prep.model_copy(update={"id": "rep-old", "candidates": rest}))
    report_store.add(
        prep.model_copy(update={"id": "rep-digest", "kind": "digest", "candidates": [first]})
    )
    calls = []

    class FakeWatcher:
        def __init__(self, client, store, publish):
            pass

        async def run_once(self, profile, shortlist):
            calls.append(shortlist)
            return []

    monkeypatch.setattr(watcher_run, "Watcher", FakeWatcher)

    await runtime.watcher_job()

    assert sorted(calls[0]) == sorted(c.entity_id for c in prep.candidates)


def test_since_last_prep_stops_at_the_latest_prep():
    base = fixtures.latest_report()
    for rid, kind in [("p1", "prep"), ("d1", "digest"), ("p2", "prep"), ("d2", "digest")]:
        report_store.add(base.model_copy(update={"id": rid, "kind": kind}))

    assert [r.id for r in report_store.since_last_prep()] == ["d2", "p2"]


async def test_watcher_job_survives_a_cache_miss(monkeypatch):
    report_store.add(fixtures.latest_report())

    class MissingWatcher:
        def __init__(self, *args, **kwargs):
            pass

        async def run_once(self, profile, shortlist):
            raise CalaCacheMiss("not warmed")

    monkeypatch.setattr(watcher_run, "Watcher", MissingWatcher)

    await runtime.watcher_job()


def test_simulated_event_is_scored_against_the_stored_profile(client, monkeypatch):
    seen = []

    class FakeWatcher:
        def __init__(self, client, store, publish):
            pass

        async def simulate(self, name, profile):
            seen.append(profile)
            return []

    monkeypatch.setattr("app.api.demo.Watcher", FakeWatcher)

    response = client.post("/api/demo/simulate-event", json={"fixture": "grei_seed_round"})

    assert response.json()["error"]["code"] == "no_alert"
    assert seen == [profile_store.current()]


def _live_without_key(monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("CALA_MODE", "live")
    monkeypatch.setenv("CALA_API_KEY", "")
    get_settings.cache_clear()


async def test_no_cala_key_in_live_mode_falls_back_to_fixture_candidates(monkeypatch):
    _live_without_key(monkeypatch)
    result = await sources.candidates_for(profile_store.current())
    assert [c.entity_id for c in result] == [c.entity_id for c in sources.fixture_candidates()]


def test_chat_and_reports_work_on_a_fresh_checkout_without_cala_key(client, monkeypatch):
    _live_without_key(monkeypatch)
    assert client.post("/api/chat", json={"text": "hello"}).status_code == 200
    assert client.post("/api/reports/run", json={"kind": "prep"}).status_code == 200


async def test_watcher_job_skips_quietly_without_cala_key(monkeypatch):
    report_store.add(fixtures.latest_report())
    _live_without_key(monkeypatch)
    await runtime.watcher_job()

"""Each demo visitor's anonymous workspace keeps its own profile, chat, reports and alerts."""

import asyncio
import json
import sqlite3
from datetime import UTC, datetime

from app import fixtures, runtime, workspace
from app.events import EventBus
from app.llm.fake import FakeLLM
from app.models import ReportRef
from app.reports import service
from app.store import db
from app.store import reports as report_store
from app.store.profile import default_profile
from app.store.snapshots import WatchStore
from app.watcher import run as watcher_run

A = {"X-Workspace": "visitor-a"}
B = {"X-Workspace": "visitor-b"}


def test_a_chat_correction_stays_in_its_workspace(client):
    client.post("/api/chat", json={"text": "hello"}, headers=A)
    client.post("/api/chat", json={"text": "No B2C please"}, headers=A)

    assert client.get("/api/profile", headers=A).json()["filters"]["sectors_out"] == ["B2C"]
    assert client.get("/api/profile", headers=B).json()["version"] == 1
    assert client.get("/api/profile/history", headers=B).json() == []
    assert client.get("/api/chat", headers=B).json() == []
    assert len(client.get("/api/chat", headers=A).json()) == 4


def test_undo_only_reverts_the_callers_workspace(client):
    for headers in (A, B):
        client.post("/api/chat", json={"text": "hello"}, headers=headers)
        client.post("/api/chat", json={"text": "No B2C please"}, headers=headers)

    assert client.post("/api/profile/undo", headers=A).json()["version"] == 1
    assert client.get("/api/profile", headers=B).json()["version"] == 2


def test_requests_without_a_workspace_use_the_default_one(client):
    client.post("/api/chat", json={"text": "hello"})

    default = client.get("/api/chat", headers={"X-Workspace": "default"}).json()
    assert client.get("/api/chat").json() == default and len(default) == 2
    assert client.get("/api/chat", headers=A).json() == []


def test_the_query_parameter_names_the_workspace_for_event_streams(client):
    client.post("/api/chat", json={"text": "hello"}, headers=A)

    assert len(client.get("/api/chat?workspace=visitor-a").json()) == 2


def test_a_malformed_workspace_is_rejected_with_the_error_shape(client):
    response = client.get("/api/profile", headers={"X-Workspace": "../../etc"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_workspace"


async def test_events_only_reach_subscribers_of_the_same_workspace():
    bus = EventBus()
    with workspace.use("visitor-a"):
        mine = bus.subscribe()
    with workspace.use("visitor-b"):
        other = bus.subscribe()
        reached = bus.publish("report", ReportRef(id="rep-b"))

    assert reached == 1
    event = await asyncio.wait_for(other.get(), timeout=1)
    assert json.loads(event.data) == {"id": "rep-b"}
    assert mine._queue.empty()
    mine.close()
    other.close()


async def test_a_rebuild_in_one_workspace_does_not_supersede_another(now):
    with workspace.use("visitor-a"):
        first = service.schedule_rebuild(default_profile(now), llm=FakeLLM())
    with workspace.use("visitor-b"):
        second = service.schedule_rebuild(default_profile(now), llm=FakeLLM())
    await service.wait_idle()

    with workspace.use("visitor-a"):
        assert report_store.latest().id == first
    with workspace.use("visitor-b"):
        assert report_store.latest().id == second
    assert report_store.latest() is None


def test_alerts_and_snapshots_are_kept_per_workspace():
    alert = fixtures.alerts()[0]
    taken = datetime(2026, 11, 14, tzinfo=UTC)
    with db.connect() as conn:
        with workspace.use("visitor-a"):
            WatchStore(conn).add_alert(alert)
            WatchStore(conn).save_snapshot("ent-1", {"headcount": 10}, taken)
        with workspace.use("visitor-b"):
            store = WatchStore(conn)
            assert store.alerts() == []
            assert store.snapshot("ent-1") is None
            store.add_alert(alert)
            assert [a.id for a in store.alerts()] == [alert.id]


def test_get_alerts_reads_the_callers_workspace(client):
    with workspace.use("visitor-a"), db.connect() as conn:
        WatchStore(conn).add_alert(fixtures.alerts()[0].model_copy(update={"id": "alr-mine"}))

    ids_a = [a["id"] for a in client.get("/api/alerts", headers=A).json()]
    ids_b = [a["id"] for a in client.get("/api/alerts", headers=B).json()]

    assert ids_a == ["alr-mine"]
    assert "alr-mine" not in ids_b


async def test_the_watcher_job_checks_every_workspace_with_a_report(monkeypatch):
    report = fixtures.latest_report()
    for owner in ("visitor-a", "visitor-b"):
        with workspace.use(owner):
            report_store.add(report.model_copy(update={"id": f"rep-{owner}"}))
    seen = []

    class FakeWatcher:
        def __init__(self, client, store, publish):
            pass

        async def run_once(self, profile, shortlist):
            seen.append(workspace.current())
            return []

    monkeypatch.setattr(watcher_run, "Watcher", FakeWatcher)

    await runtime.watcher_job()

    assert seen == ["visitor-a", "visitor-b"]


async def test_the_digest_job_runs_for_every_workspace_with_a_report(monkeypatch):
    for owner in ("visitor-a", "visitor-b"):
        with workspace.use(owner):
            report_store.add(fixtures.latest_report().model_copy(update={"id": f"rep-{owner}"}))
    ran = []

    async def fake_run(kind, **kwargs):
        ran.append((kind, workspace.current()))
        return fixtures.latest_report()

    monkeypatch.setattr(service, "run", fake_run)

    await runtime.digest_job()

    assert ran == [("digest", "visitor-a"), ("digest", "visitor-b")]


def test_an_older_database_drops_visitor_tables_but_keeps_the_cala_cache(tmp_path):
    path = tmp_path / "old.db"
    with sqlite3.connect(path) as conn:
        conn.execute("CREATE TABLE reports (seq INTEGER PRIMARY KEY, id TEXT, report_json TEXT)")
        conn.execute("INSERT INTO reports VALUES (1, 'rep-old', '{}')")
        conn.execute("CREATE TABLE cala_keep (key TEXT)")
        conn.execute("INSERT INTO cala_keep VALUES ('warm')")
    conn.close()

    db.init_db(path)

    with db.connect(path) as conn:
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(reports)")}
        assert "workspace" in columns
        assert conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 0
        assert conn.execute("SELECT key FROM cala_keep").fetchone()[0] == "warm"

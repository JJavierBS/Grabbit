import json

import respx

from app import workspace
from app.config import get_settings
from app.events import bus
from app.reports.service import wait_idle
from tests.test_discovery import NORTHWIND, graph  # noqa: F401
from tests.test_warm import serve


@respx.mock
def test_thesis_report_correction_and_shortlisted_alert_share_one_workspace(
    client,
    monkeypatch,
    graph,  # noqa: F811
):
    monkeypatch.setenv("CALA_MODE", "live")
    monkeypatch.setenv("CALA_API_KEY", "test-key")
    monkeypatch.setenv("CONTEXT_DEV_API_KEY", "")
    get_settings.cache_clear()
    serve(graph)
    headers = {"X-Workspace": "demo-rehearsal"}

    thesis = client.post(
        "/api/chat", json={"text": "I am looking for Nordic B2B startups"}, headers=headers
    )
    assert thesis.status_code == 200
    assert thesis.json()["questions"]
    client.portal.call(wait_idle)

    prep = client.post("/api/reports/run", json={"kind": "prep"}, headers=headers)
    assert prep.status_code == 200
    original = prep.json()
    startup = next(c for c in original["candidates"] if c["entity_id"] == NORTHWIND)
    assert any(
        source["url"].startswith("https://")
        for round_ in startup["rounds"]
        for fact in (round_["amount"], round_["date"])
        for source in fact["sources"]
        if source["url"]
    )

    correction = client.post(
        "/api/chat", json={"text": "Shorter, co-investors first"}, headers=headers
    )
    assert correction.status_code == 200
    client.portal.call(wait_idle)
    rewritten = client.get("/api/reports/latest", headers=headers).json()
    profile = client.get("/api/profile", headers=headers).json()
    assert rewritten["id"] != original["id"]
    assert rewritten["profile_version"] > original["profile_version"]
    assert rewritten["summary"] != original["summary"]
    assert profile["style"]["length"] == "short"
    assert profile["instructions"]
    assert client.get("/api/profile/history", headers=headers).json()
    shortlisted = {c["entity_id"] for c in rewritten["candidates"]}

    with workspace.use("demo-rehearsal"), bus.subscribe() as subscription:
        response = client.post(
            "/api/demo/simulate-event", json={"fixture": "example_new_round"}, headers=headers
        )
        assert response.status_code == 200
        alert = response.json()
        event = subscription._queue.get_nowait()

    assert alert["simulated"] is True
    assert alert["entity_id"] in shortlisted
    assert alert["facts"] and alert["why_it_matters"]
    assert event.kind == "alert"
    assert json.loads(event.data)["id"] == alert["id"]
    assert client.get("/api/alerts", headers=headers).json()[0]["id"] == alert["id"]
    assert client.get("/api/reports/latest", headers=headers).json() == rewritten
    other = {"X-Workspace": "another-visitor"}
    assert client.get("/api/chat", headers=other).json() == []
    assert client.get("/api/reports/latest", headers=other).status_code == 404

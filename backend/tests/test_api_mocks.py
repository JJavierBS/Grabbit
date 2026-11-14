"""One check per router: each endpoint answers with its api.md shape."""

from app.events import bus
from app.models import Alert, ChatMessage, Profile, ProfileChange, Report


def test_profile_endpoints(client):
    profile = Profile.model_validate(client.get("/api/profile").json())
    history = [
        ProfileChange.model_validate(item) for item in client.get("/api/profile/history").json()
    ]

    assert profile.version == 1
    assert history == []
    # Real since #25: a fresh profile has nothing to undo.
    assert client.post("/api/profile/undo").status_code == 409


def test_chat_endpoints(client):
    reply = client.post("/api/chat", json={"text": "Skip hardware"})
    conversation = client.get("/api/chat").json()

    assert reply.status_code == 200
    message = ChatMessage.model_validate(reply.json())
    assert message.role == "agent"
    assert [ChatMessage.model_validate(item).role for item in conversation] == ["user", "agent"]


def test_reports_endpoints(client):
    latest = Report.model_validate(client.get("/api/reports/latest").json())
    run = client.post("/api/reports/run", json={"kind": "digest"})

    assert latest.candidates
    assert run.status_code == 200
    new_report = Report.model_validate(run.json())
    assert new_report.kind == "digest"
    assert new_report.id != latest.id


def test_reports_run_publishes_report_event(client):
    with bus.subscribe() as subscription:
        report_id = client.post("/api/reports/run", json={"kind": "prep"}).json()["id"]
        event = subscription._queue.get_nowait()

    assert event.kind == "report"
    assert report_id in event.data


def test_alerts_endpoint_newest_first(client):
    alerts = [Alert.model_validate(item) for item in client.get("/api/alerts").json()]

    assert len(alerts) >= 2
    assert [a.created_at for a in alerts] == sorted((a.created_at for a in alerts), reverse=True)


def test_simulate_event_returns_simulated_alert_and_publishes_it(client):
    with bus.subscribe() as subscription:
        response = client.post("/api/demo/simulate-event", json={"fixture": "polar_ledger_seed"})
        event = subscription._queue.get_nowait()

    assert response.status_code == 200
    alert = Alert.model_validate(response.json())
    assert alert.simulated is True
    assert event.kind == "alert"
    assert alert.id in event.data


def test_simulate_event_unknown_fixture(client):
    response = client.post("/api/demo/simulate-event", json={"fixture": "nope"})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "fixture_not_found"


def test_simulate_event_rejects_path_like_fixture_names(client):
    response = client.post("/api/demo/simulate-event", json={"fixture": "../profile"})

    assert response.status_code == 422


def test_simulate_event_disabled_without_demo_mode(client, monkeypatch):
    from app.config import get_settings

    monkeypatch.setenv("DEMO_MODE", "0")
    get_settings.cache_clear()

    response = client.post("/api/demo/simulate-event", json={"fixture": "polar_ledger_seed"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "demo_mode_disabled"

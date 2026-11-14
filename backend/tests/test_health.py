import pytest

from app.config import get_settings


def test_health_reports_modes(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "cala_mode": "replay",
        "llm_mode": "fake",
        "demo_mode": True,
    }


def test_health_follows_environment(client, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CALA_MODE", "live")
    monkeypatch.setenv("LLM_MODE", "gemini")
    monkeypatch.setenv("DEMO_MODE", "0")
    get_settings.cache_clear()

    body = client.get("/api/health").json()

    assert (body["cala_mode"], body["llm_mode"], body["demo_mode"]) == ("live", "gemini", False)


def test_openapi_is_published_under_api(client):
    schema = client.get("/api/openapi.json").json()

    assert "/api/reports/latest" in schema["paths"]
    assert {"Fact", "Candidate", "Report", "Alert", "ErrorResponse"} <= set(
        schema["components"]["schemas"]
    )


def test_scheduler_runs_during_app_lifetime(client):
    assert client.app.state.scheduler.running

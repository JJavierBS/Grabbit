from fastapi.testclient import TestClient

from app.main import app


def client() -> TestClient:
    return TestClient(app)


def test_chat_round_trip_changes_profile_and_history():
    c = client()
    assert c.post("/api/chat", json={"text": "hello"}).status_code == 200
    reply = c.post("/api/chat", json={"text": "No B2C please"}).json()
    assert reply["role"] == "agent"
    assert reply["profile_changes"][0]["field"] == "filters.sectors_out"

    profile = c.get("/api/profile").json()
    assert profile["version"] == 2 and profile["filters"]["sectors_out"] == ["B2C"]
    history = c.get("/api/profile/history").json()
    assert history[0]["after"] == ["B2C"] and history[0]["reason"] == "no B2C startups"
    assert [m["role"] for m in c.get("/api/chat").json()] == ["user", "agent", "user", "agent"]


def test_undo_reverts_one_version():
    c = client()
    c.post("/api/chat", json={"text": "hello"})
    c.post("/api/chat", json={"text": "No B2C please"})
    profile = c.post("/api/profile/undo").json()
    assert profile["version"] == 1 and profile["filters"]["sectors_out"] == []
    assert c.get("/api/profile/history").json() == []


def test_undo_without_changes_uses_error_shape():
    response = client().post("/api/profile/undo")
    assert response.status_code == 409
    assert response.json() == {
        "error": {"code": "nothing_to_undo", "message": "The profile has no change to undo."}
    }


def test_empty_chat_message_is_rejected():
    response = client().post("/api/chat", json={"text": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"


def test_health_reports_modes():
    assert client().get("/api/health").json()["llm_mode"] == "fake"

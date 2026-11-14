def test_chat_round_trip_changes_profile_and_history(client):
    assert client.post("/api/chat", json={"text": "hello"}).status_code == 200
    reply = client.post("/api/chat", json={"text": "No B2C please"}).json()
    assert reply["role"] == "agent"
    assert reply["profile_changes"][0]["field"] == "filters.sectors_out"

    profile = client.get("/api/profile").json()
    assert profile["version"] == 2 and profile["filters"]["sectors_out"] == ["B2C"]
    history = client.get("/api/profile/history").json()
    assert history[0]["after"] == ["B2C"] and history[0]["reason"] == "no B2C startups"
    roles = [m["role"] for m in client.get("/api/chat").json()]
    assert roles == ["user", "agent", "user", "agent"]


def test_undo_reverts_one_version(client):
    client.post("/api/chat", json={"text": "hello"})
    client.post("/api/chat", json={"text": "No B2C please"})
    profile = client.post("/api/profile/undo").json()
    assert profile["version"] == 1 and profile["filters"]["sectors_out"] == []
    assert client.get("/api/profile/history").json() == []


def test_undo_without_changes_uses_error_shape(client):
    response = client.post("/api/profile/undo")
    assert response.status_code == 409
    assert response.json() == {
        "error": {"code": "nothing_to_undo", "message": "The profile has no change to undo."}
    }


def test_empty_chat_message_is_rejected(client):
    response = client.post("/api/chat", json={"text": ""})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_a_chat_turn_starts_by_reporting_the_cala_walk(client, published):
    client.post("/api/chat", json={"text": "hello"})
    progress = [payload for kind, payload in published if kind == "progress"]
    assert progress[0].phase == "cala"
    assert progress[0].label == "Walking the Slush attendees in Cala…"

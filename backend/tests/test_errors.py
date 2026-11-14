def _assert_error_shape(response, status: int, code: str) -> None:
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == code
    assert body["error"]["message"]


def test_unknown_api_path_uses_error_shape(client):
    _assert_error_shape(client.get("/api/does-not-exist"), 404, "not_found")


def test_invalid_body_uses_error_shape(client):
    _assert_error_shape(client.post("/api/chat", json={"text": ""}), 422, "validation_error")


def test_missing_body_uses_error_shape(client):
    _assert_error_shape(client.post("/api/reports/run"), 422, "validation_error")


def test_unknown_enum_value_is_rejected(client):
    response = client.post("/api/reports/run", json={"kind": "weekly"})
    _assert_error_shape(response, 422, "validation_error")
    assert "kind" in response.json()["error"]["message"]

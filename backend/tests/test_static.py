"""The production image serves the built web app from FastAPI (Dockerfile stage 2)."""

from fastapi.testclient import TestClient

from app import main


def test_built_frontend_is_served_at_root_and_api_still_wins(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<title>Grabbit</title>")
    monkeypatch.setattr(main, "FRONTEND_DIST", tmp_path)

    with TestClient(main.create_app()) as client:
        page = client.get("/")
        health = client.get("/api/health")
        missing_api = client.get("/api/nope")

    assert page.status_code == 200
    assert "<title>Grabbit</title>" in page.text
    assert health.json()["status"] == "ok"
    assert missing_api.json()["error"]["code"] == "not_found"


def test_api_runs_without_a_built_frontend(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "FRONTEND_DIST", tmp_path / "missing")

    with TestClient(main.create_app()) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/").status_code == 404

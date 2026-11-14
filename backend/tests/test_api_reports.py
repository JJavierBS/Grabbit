from fastapi.testclient import TestClient

from app import events
from app.llm.fake import FakeLLM
from app.llm.scoring import score_alert
from app.main import app
from app.models import Alert, Profile


def test_run_then_latest_and_report_event():
    c = TestClient(app)
    report = c.post("/api/reports/run", json={"kind": "prep"}).json()
    assert report["kind"] == "prep" and report["summary"]
    assert c.get("/api/reports/latest").json()["id"] == report["id"]
    assert ("report", {"id": report["id"]}) in events.recent()


def test_latest_without_report_uses_error_shape():
    response = TestClient(app).get("/api/reports/latest")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "no_report"


def test_chat_correction_regenerates_the_report():
    c = TestClient(app)
    first = c.post("/api/reports/run", json={"kind": "prep"}).json()
    c.post("/api/chat", json={"text": "hello"})
    reply = c.post("/api/chat", json={"text": "Shorter, co-investors first"}).json()

    latest = c.get("/api/reports/latest").json()
    assert reply["report_id"] == latest["id"] != first["id"]
    assert latest["profile_version"] == 2
    assert latest["summary"] == "Co-investments first: 5 startups, kept short."


def test_undo_regenerates_the_report():
    c = TestClient(app)
    c.post("/api/chat", json={"text": "hello"})
    c.post("/api/chat", json={"text": "No B2C please"})
    assert len(c.get("/api/reports/latest").json()["candidates"]) == 4
    c.post("/api/profile/undo")
    assert len(c.get("/api/reports/latest").json()["candidates"]) == 6


async def test_score_alert(now):
    alert = Alert(
        id="a1",
        created_at=now,
        entity_id="cand-kiln",
        entity_name="Kiln Analytics",
        kind="new_round",
        title="New round",
        why_it_matters="North Pine led it",
        importance=0,
    )
    profile = Profile(updated_at=now)
    assert await score_alert(FakeLLM(), alert, profile) == (
        0.9,
        "A reference investor led a new round in a shortlisted startup.",
    )
    score, reason = await score_alert(FakeLLM(scripts=[]), alert, profile)
    assert score == 0.5 and reason.startswith("Not scored")

from app.llm.fake import FakeLLM
from app.llm.scoring import score_alert
from app.models import Alert, ReportRef
from app.reports import service
from app.store.profile import default_profile


def settle(client):
    client.portal.call(service.wait_idle)


def test_run_then_latest_and_report_event(client, published):
    report = client.post("/api/reports/run", json={"kind": "prep"}).json()
    assert report["kind"] == "prep" and report["summary"]
    assert client.get("/api/reports/latest").json()["id"] == report["id"]
    assert ("report", ReportRef(id=report["id"])) in published


def test_latest_without_report_uses_error_shape(client):
    response = client.get("/api/reports/latest")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "no_report"


def test_chat_correction_regenerates_the_report(client):
    first = client.post("/api/reports/run", json={"kind": "prep"}).json()
    client.post("/api/chat", json={"text": "hello"})
    reply = client.post("/api/chat", json={"text": "Shorter, co-investors first"}).json()
    settle(client)

    latest = client.get("/api/reports/latest").json()
    assert reply["report_id"] == latest["id"] != first["id"]
    assert latest["profile_version"] == 2
    assert latest["summary"] == "Co-investments first: 5 startups, kept short."


def test_undo_regenerates_the_report(client):
    client.post("/api/chat", json={"text": "hello"})
    client.post("/api/chat", json={"text": "No B2C please"})
    settle(client)
    assert len(client.get("/api/reports/latest").json()["candidates"]) == 4
    client.post("/api/profile/undo")
    settle(client)
    assert len(client.get("/api/reports/latest").json()["candidates"]) == 6


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
        facts=[],
        simulated=False,
    )
    profile = default_profile(now)
    assert await score_alert(FakeLLM(), alert, profile) == (
        0.9,
        "A reference investor led a new round in a shortlisted startup.",
    )
    score, reason = await score_alert(FakeLLM(scripts=[]), alert, profile)
    assert score == 0.5 and reason.startswith("Not scored")


def test_list_reports_newest_first(client):
    assert client.get("/api/reports").json() == []
    first = client.post("/api/reports/run", json={"kind": "prep"}).json()
    second = client.post("/api/reports/run", json={"kind": "digest"}).json()
    assert [r["id"] for r in client.get("/api/reports").json()] == [second["id"], first["id"]]

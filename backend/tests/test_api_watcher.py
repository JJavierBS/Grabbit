import copy

import pytest

from app.events import bus
from app.models import Alert
from tests.conftest import load_cala

NORTHWIND = "c0000000-0000-4000-8000-000000000001"
SEED = "r0000000-0000-4000-8000-000000000001"


class FakeCala:
    """Stands in for CalaClient inside the route: serves the example startup and its round."""

    def __init__(self, *args, **kwargs):
        self.company = load_cala("company_startup")

    async def introspect(self, entity_id):
        rels = self.company["relationships"]
        return {
            "properties": list(self.company["properties"]),
            "relationships": {d: list(rels[d]) for d in ("incoming", "outgoing")},
            "numerical_observations": {},
        }

    async def retrieve(self, entity_id, body=None, fresh=False):
        if entity_id == NORTHWIND:
            return copy.deepcopy(self.company)
        if entity_id == SEED:
            return load_cala("round_seed")
        raise KeyError(entity_id)

    async def aclose(self):
        return None


@pytest.fixture
def fake_cala(monkeypatch):
    monkeypatch.setattr("app.api.demo.CalaClient", FakeCala)


def test_staged_change_goes_through_the_watcher(client, fake_cala):
    with bus.subscribe() as subscription:
        response = client.post("/api/demo/simulate-event", json={"fixture": "example_ceo_leaves"})
        event = subscription._queue.get_nowait()

    assert response.status_code == 200
    alert = Alert.model_validate(response.json())
    assert (alert.kind, alert.simulated, alert.importance) == ("executive_change", True, 0.85)
    assert alert.facts[0].value == "2026-11-13"
    assert event.kind == "alert" and alert.id in event.data

    stored = client.get("/api/alerts").json()
    assert [a["id"] for a in stored] == [alert.id]


def test_staged_event_can_be_replayed_in_rehearsals(client, fake_cala):
    first = client.post("/api/demo/simulate-event", json={"fixture": "example_ceo_leaves"})
    second = client.post("/api/demo/simulate-event", json={"fixture": "example_ceo_leaves"})
    assert first.status_code == second.status_code == 200
    assert first.json()["id"] != second.json()["id"]


def test_staged_change_without_cache_says_how_to_fix_it(client):
    response = client.post("/api/demo/simulate-event", json={"fixture": "example_new_round"})
    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "cache_miss"
    assert "make warm" in error["message"]


def test_alerts_fall_back_to_fixtures_until_the_watcher_stores_some(client):
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert len(response.json()) >= 2

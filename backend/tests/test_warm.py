"""`make warm` covers the first chat turn on the demo, and `--check` proves it (#119)."""

import json

import httpx
import respx

from app.agent.sources import MAX_ATTENDEES, event_walk_limits
from app.cala.client import BASE_URL, CalaClient, CalaLimiter
from app.discovery.pipeline import SLUSH_2026
from scripts.warm import first_turn_misses, warm_first_turn
from tests.test_discovery import FakeCala, graph  # noqa: F401  (graph is a fixture)


def serve(nodes: dict) -> None:
    """Answer Cala's HTTP API from a dict of nodes, the way FakeCala does in memory. Ids the
    fixture only mentions (co-investors) answer as bare organisations, as Cala would."""

    def node(entity_id: str) -> dict:
        bare = {"id": entity_id, "name": entity_id, "entity_type": "Organization"}
        return nodes.setdefault(entity_id, {**bare, "properties": {}, "relationships": {}})

    fake = FakeCala(nodes)

    async def introspection(request: httpx.Request, entity_id: str) -> httpx.Response:
        node(entity_id)
        return httpx.Response(200, json=await fake.introspect(entity_id))

    async def entity(request: httpx.Request, entity_id: str) -> httpx.Response:
        node(entity_id)
        body = json.loads(request.content or b"{}")
        return httpx.Response(200, json=await fake.retrieve(entity_id, body))

    respx.get(url__regex=rf"{BASE_URL}/v1/entities/(?P<entity_id>[^/]+)/introspection").mock(
        side_effect=introspection
    )
    respx.post(url__regex=rf"{BASE_URL}/v1/entities/(?P<entity_id>[^/]+)$").mock(side_effect=entity)


def test_warm_replays_the_same_walk_as_the_chat():
    assert event_walk_limits().max_attendees == MAX_ATTENDEES


@respx.mock
async def test_after_warm_the_first_chat_turn_has_no_cache_miss(cache, graph):  # noqa: F811
    serve(graph)
    calls, misses = await first_turn_misses(cache, SLUSH_2026)
    assert misses > 0  # a fresh workspace on a cold cache

    live = CalaClient("key", cache, limiter=CalaLimiter())
    await warm_first_turn(live, SLUSH_2026)
    await live.aclose()

    calls, misses = await first_turn_misses(cache, SLUSH_2026)
    assert calls > 0
    assert misses == 0


async def test_check_exits_non_zero_on_a_cold_cache(monkeypatch, tmp_path, capsys):
    import argparse

    from scripts import warm

    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "cold.db"))
    code = await warm.main(argparse.Namespace(check=True, event=SLUSH_2026))
    assert code == 1
    assert "cache misses" in capsys.readouterr().out


@respx.mock
async def test_an_entity_cala_does_not_know_is_no_miss_after_warm(cache, graph):  # noqa: F811
    """#149: a 404 met while warming is cached, so the check does not count it."""
    # Registered first, so it wins over the catch-all routes of `serve`.
    gone = respx.get(f"{BASE_URL}/v1/entities/kide/introspection").mock(
        return_value=httpx.Response(404, json={"error": "not_found"})
    )
    serve(graph)
    live = CalaClient("key", cache, limiter=CalaLimiter())
    await warm_first_turn(live, SLUSH_2026)
    await live.aclose()
    assert gone.call_count == 1
    calls, misses = await first_turn_misses(cache, SLUSH_2026)
    assert calls > 0 and misses == 0

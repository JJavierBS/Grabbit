"""`make warm` covers the first chat turn on the demo, and `--check` proves it (#119)."""

import json

import httpx
import respx

from app.agent.sources import MAX_ATTENDEES, event_walk_limits
from app.cala.client import BASE_URL, CalaClient, CalaLimiter
from app.discovery.pipeline import SLUSH_2026
from app.discovery.reverse import CoInvestor, ReverseResult, ReverseStats
from app.models import ReferenceInvestor
from scripts.warm import (
    first_turn_misses,
    reverse_summary,
    reverse_walk_misses,
    warm_first_turn,
    warm_references,
    warm_reverse_walk,
)
from tests.test_discovery import AURORA, FakeCala, graph  # noqa: F401  (graph is a fixture)

AURORA_REF = ReferenceInvestor(entity_id="unresolved:aurora ventures", name="Aurora Ventures")


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
    out = capsys.readouterr().out
    assert "cache misses" in out
    assert "reverse walk: 1 Cala calls, 1 cache misses" in out


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


@respx.mock
async def test_after_warm_the_reverse_walk_has_no_cache_miss(cache, graph):  # noqa: F811
    serve(graph)
    stubs = [{"id": AURORA, "name": "Aurora Ventures", "entity_type": "Organization"}]
    respx.get(f"{BASE_URL}/v1/entities").mock(
        return_value=httpx.Response(200, json={"entities": stubs})
    )
    calls, misses = await reverse_walk_misses(cache, SLUSH_2026, [AURORA_REF])
    assert misses > 0

    live = CalaClient("key", cache, limiter=CalaLimiter())
    reached = await warm_reverse_walk(live, SLUSH_2026, [AURORA_REF])
    await live.aclose()

    assert [c.name for c in reached.candidates] == ["Northwind Robotics"]
    assert reached.stats.startups == 1
    calls, misses = await reverse_walk_misses(cache, SLUSH_2026, [AURORA_REF])
    assert calls > 0
    assert misses == 0


def test_warm_prints_what_the_second_ring_walked_and_added():
    reverse = ReverseResult(
        co_investors=[CoInvestor("Pioneer Fund", ["p-1", "p-2"], 16, "Y Combinator")],
        stats=ReverseStats(
            startups=9,
            co_investors=311,
            co_investors_walked=7,
            co_investors_skipped=2,
            second_ring_startups=4,
        ),
    )

    lines = reverse_summary(reverse, [AURORA_REF])

    assert "co-investors seen 311  walked 7  hubs skipped 2" in lines
    assert "strongest co-investors (shared rounds): Pioneer Fund 16" in lines
    assert "attending startups added by the second ring 4" in lines


def test_warm_walks_the_second_ring_without_a_call_budget(monkeypatch):
    import asyncio

    from scripts import warm

    seen = []

    async def fake_reverse_walk(client, references, event_id=None, today=None, limits=None):
        seen.append(limits)
        return ReverseResult()

    monkeypatch.setattr(warm, "reverse_walk", fake_reverse_walk)
    asyncio.run(warm_reverse_walk(None, SLUSH_2026, [AURORA_REF]))

    assert seen[0].call_budget is None and seen[0].second_ring is True


def test_warm_covers_the_demo_investors_and_the_stored_profile_once_each():
    from app.store import profile as profile_store

    stored = profile_store.current().model_copy(
        update={
            "reference_investors": [
                ReferenceInvestor(entity_id="inv-1", name="y combinator"),
                AURORA_REF,
            ]
        }
    )
    profile_store.save_version(stored, [])

    assert [r.name for r in warm_references()] == ["Y Combinator", "500 Global", "Aurora Ventures"]

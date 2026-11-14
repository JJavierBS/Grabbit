import json
from datetime import UTC, datetime

import httpx

from app.context_dev.client import ContextDevClient

SINCE = datetime(2026, 8, 16, tzinfo=UTC)
ARTICLE = {
    "id": "a1",
    "story_id": "s1",
    "title": "Kiln raises a seed round",
    "url": "https://n.example/a1",
}


def _client(handler, **kwargs):
    seen = []

    def record(request):
        seen.append(request)
        return handler(request)

    defaults = {"api_key": "test-key", "transport": httpx.MockTransport(record)}
    return ContextDevClient(**(defaults | kwargs)), seen


async def _search(client, **kwargs):
    args = {"domain": "kiln.fi", "name": "Kiln", "source_domains": [], "since": SINCE} | kwargs
    return await client.search_news(**args)


async def test_request_shape_and_allow_list():
    client, seen = _client(lambda r: httpx.Response(200, json={"data": [ARTICLE]}))
    articles = await _search(client, source_domains=["a.com", "b.com", "c.com", "d.com"])

    assert articles == [ARTICLE]
    request = seen[0]
    assert request.url.path == "/v1/news/search"
    assert request.headers["authorization"] == "Bearer test-key"
    body = json.loads(request.content)
    assert body["searchBy"] == {"type": "entity", "entity": {"type": "domain", "domain": "kiln.fi"}}
    assert body["filterBy"]["sourceDomain"] == ["a.com", "b.com", "c.com"]
    assert body["filterBy"]["date"]["from"] == int(SINCE.timestamp() * 1000)


async def test_name_search_without_domain():
    client, seen = _client(lambda r: httpx.Response(200, json={"data": []}))
    await _search(client, domain=None)
    body = json.loads(seen[0].content)
    assert body["searchBy"]["entity"] == {"type": "name", "name": "Kiln"}
    assert "sourceDomain" not in body["filterBy"]


async def test_second_call_is_served_from_cache():
    client, seen = _client(lambda r: httpx.Response(200, json={"data": [ARTICLE]}))
    await _search(client)
    assert await _search(client) == [ARTICLE]
    assert len(seen) == 1


async def test_retries_once_on_rate_limit():
    responses = iter([httpx.Response(429), httpx.Response(200, json={"data": [ARTICLE]})])
    client, seen = _client(lambda r: next(responses))
    assert await _search(client) == [ARTICLE]
    assert len(seen) == 2


async def test_errors_degrade_to_no_signals():
    client, seen = _client(lambda r: httpx.Response(500))
    assert await _search(client) == []
    assert len(seen) == 2
    client, _ = _client(lambda r: httpx.Response(402, json={"error": "USAGE_EXCEEDED"}))
    assert await _search(client) == []


async def test_network_failure_degrades_to_no_signals():
    def boom(request):
        raise httpx.ConnectError("offline")

    client, _ = _client(boom)
    assert await _search(client) == []


async def test_without_key_nothing_is_called():
    client, seen = _client(lambda r: httpx.Response(200, json={"data": [ARTICLE]}), api_key="")
    assert not client.enabled
    assert await _search(client) == [] and seen == []


async def test_offline_reads_only_the_cache():
    online, _ = _client(lambda r: httpx.Response(200, json={"data": [ARTICLE]}))
    await _search(online)
    offline, seen = _client(lambda r: httpx.Response(200, json={"data": []}), offline=True)
    assert await _search(offline) == [ARTICLE]
    assert await _search(offline, domain="other.fi") == []
    assert seen == []

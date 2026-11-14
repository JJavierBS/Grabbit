import httpx
import pytest
import respx

from app.cala.client import BASE_URL, CalaCacheMiss, CalaClient, CalaError
from app.store.cala_cache import cache_key
from tests.conftest import load_cala

COMPANY_ID = "c0000000-0000-4000-8000-000000000001"


class FakeSleep:
    def __init__(self):
        self.delays: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.delays.append(delay)


def make_client(cache, **kwargs) -> CalaClient:
    kwargs.setdefault("sleep", FakeSleep())
    return CalaClient("test-key", cache, **kwargs)


@respx.mock
async def test_retrieve_sends_key_and_caches(cache):
    route = respx.post(f"{BASE_URL}/v1/entities/{COMPANY_ID}").mock(
        return_value=httpx.Response(200, json=load_cala("company_startup"))
    )
    client = make_client(cache)
    body = {"properties": ["name"]}
    first = await client.retrieve(COMPANY_ID, body)
    second = await client.retrieve(COMPANY_ID, body)
    assert first == second
    assert route.call_count == 1
    assert route.calls[0].request.headers["X-API-KEY"] == "test-key"
    assert (client.calls_made, client.cache_hits) == (1, 1)


@respx.mock
async def test_different_bodies_are_cached_apart(cache):
    route = respx.post(f"{BASE_URL}/v1/entities/{COMPANY_ID}").mock(
        return_value=httpx.Response(200, json={"id": COMPANY_ID})
    )
    client = make_client(cache)
    await client.retrieve(COMPANY_ID, {"properties": ["name"]})
    await client.retrieve(COMPANY_ID, {"properties": ["website"]})
    assert route.call_count == 2


@respx.mock
async def test_429_backs_off_then_succeeds(cache):
    sleep = FakeSleep()
    respx.get(f"{BASE_URL}/v1/entities/{COMPANY_ID}/introspection").mock(
        side_effect=[
            httpx.Response(429, json={"error": "rate_limit_exceeded"}),
            httpx.Response(429, json={"error": "rate_limit_exceeded"}),
            httpx.Response(200, json={"properties": ["name"]}),
        ]
    )
    client = make_client(cache, sleep=sleep, backoff_base=0.5)
    assert await client.introspect(COMPANY_ID) == {"properties": ["name"]}
    assert sleep.delays == [0.5, 1.0]


@respx.mock
async def test_gives_up_after_max_retries(cache):
    respx.get(f"{BASE_URL}/v1/entities/{COMPANY_ID}/introspection").mock(
        return_value=httpx.Response(429, json={"error": "rate_limit_exceeded"})
    )
    client = make_client(cache, max_retries=2)
    with pytest.raises(CalaError) as err:
        await client.introspect(COMPANY_ID)
    assert err.value.status == 429
    assert client.calls_made == 3


@respx.mock
async def test_client_errors_are_not_retried(cache):
    route = respx.post(f"{BASE_URL}/v1/entities/{COMPANY_ID}").mock(
        return_value=httpx.Response(422, json={"detail": "bad body"})
    )
    with pytest.raises(CalaError):
        await make_client(cache).retrieve(COMPANY_ID, {"bad": True})
    assert route.call_count == 1


@respx.mock
async def test_lookup_unknown_returns_none(cache):
    respx.post(f"{BASE_URL}/v1/entities/lookup").mock(return_value=httpx.Response(404))
    assert await make_client(cache).lookup("lei", "UNKNOWN") is None


@respx.mock
async def test_search_passes_types_and_returns_entities(cache):
    route = respx.get(f"{BASE_URL}/v1/entities").mock(
        return_value=httpx.Response(200, json={"entities": [{"id": "x", "name": "Slush 2026"}]})
    )
    result = await make_client(cache).search("Slush 2026", ["Event"], limit=5)
    assert result == [{"id": "x", "name": "Slush 2026"}]
    params = route.calls[0].request.url.params
    assert params["entity_types"] == "Event"
    assert params["limit"] == "5"


async def test_replay_serves_cache_without_network(cache):
    body = {"properties": ["name"]}
    key = cache_key("POST", f"/v1/entities/{COMPANY_ID}", None, body)
    cache.put(key, "POST", f"/v1/entities/{COMPANY_ID}", body, {"id": COMPANY_ID})
    client = CalaClient(None, cache, mode="replay")
    with respx.mock(assert_all_called=False) as mock:
        assert await client.retrieve(COMPANY_ID, body) == {"id": COMPANY_ID}
        assert not mock.calls


async def test_replay_miss_fails_clearly(cache):
    client = CalaClient(None, cache, mode="replay")
    with pytest.raises(CalaCacheMiss):
        await client.introspect(COMPANY_ID)


def test_live_mode_requires_a_key(cache):
    with pytest.raises(ValueError):
        CalaClient(None, cache, mode="live")


@respx.mock
async def test_fresh_retrieve_skips_cached_copy_and_updates_it(cache):
    route = respx.post(f"{BASE_URL}/v1/entities/{COMPANY_ID}").mock(
        side_effect=[
            httpx.Response(200, json={"v": 1}),
            httpx.Response(200, json={"v": 2}),
        ]
    )
    client = make_client(cache)
    assert await client.retrieve(COMPANY_ID, {}) == {"v": 1}
    assert await client.retrieve(COMPANY_ID, {}, fresh=True) == {"v": 2}
    assert await client.retrieve(COMPANY_ID, {}) == {"v": 2}
    assert route.call_count == 2


@respx.mock
async def test_connection_errors_are_retried_then_become_cala_error(cache):
    sleep = FakeSleep()
    route = respx.get(f"{BASE_URL}/v1/entities/{COMPANY_ID}/introspection").mock(
        side_effect=[httpx.ConnectError("no network"), httpx.ReadError("dropped")]
    )
    client = make_client(cache, sleep=sleep, max_retries=1)
    with pytest.raises(CalaError) as err:
        await client.introspect(COMPANY_ID)
    assert err.value.status == 503
    assert route.call_count == 2 and sleep.delays == [1.0]


def test_missing_key_is_a_cala_error_so_fallbacks_catch_it(cache):
    from app.cala.client import CalaKeyMissing

    with pytest.raises(CalaError) as err:
        CalaClient("", cache, mode="live")
    assert isinstance(err.value, CalaKeyMissing) and isinstance(err.value, ValueError)

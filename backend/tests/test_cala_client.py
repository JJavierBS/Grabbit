import asyncio

import httpx
import pytest
import respx

from app.cala.client import (
    BASE_URL,
    CalaCacheMiss,
    CalaClient,
    CalaError,
    CalaLimiter,
    shared_limiter,
)
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


# The process-wide limiter (#119): the audit's first chat turn took about 200 s because Cala
# answered 429 about 100 times while several clients hit it at once.


def _slow_route(state: dict, delay: float = 0.01):
    async def answer(request: httpx.Request) -> httpx.Response:
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(delay)
        state["now"] -= 1
        return httpx.Response(200, json={"id": request.url.path.rsplit("/", 1)[-1]})

    return answer


@respx.mock
async def test_clients_share_one_limit_on_requests_in_flight(cache):
    state = {"now": 0, "peak": 0}
    respx.post(url__regex=rf"{BASE_URL}/v1/entities/.*").mock(side_effect=_slow_route(state))
    limiter = CalaLimiter(max_concurrency=1)
    chat, report = (make_client(cache, limiter=limiter) for _ in range(2))
    await asyncio.gather(
        *(chat.retrieve(f"a{i}") for i in range(6)),
        *(report.retrieve(f"b{i}") for i in range(6)),
    )
    assert state["peak"] == 1 and limiter.peak == 1
    assert chat.calls_made + report.calls_made == 12


@respx.mock
async def test_a_higher_limit_allows_that_many_at_once_and_no_more(cache):
    state = {"now": 0, "peak": 0}
    respx.post(url__regex=rf"{BASE_URL}/v1/entities/.*").mock(side_effect=_slow_route(state))
    limiter = CalaLimiter(max_concurrency=2)
    client = make_client(cache, limiter=limiter)
    await asyncio.gather(*(client.retrieve(f"e{i}") for i in range(8)))
    assert state["peak"] == 2


async def test_requests_start_at_least_the_interval_apart():
    clock = {"t": 0.0}
    starts: list[float] = []

    async def sleep(seconds: float) -> None:
        clock["t"] += seconds

    limiter = CalaLimiter(min_interval=0.25, clock=lambda: clock["t"], sleep=sleep)
    for _ in range(4):
        async with limiter:
            starts.append(clock["t"])
    assert starts == [0.0, 0.25, 0.5, 0.75]


async def test_a_429_pauses_every_client_sharing_the_limiter():
    clock = {"t": 0.0}

    async def sleep(seconds: float) -> None:
        clock["t"] += seconds

    limiter = CalaLimiter(clock=lambda: clock["t"], sleep=sleep)
    async with limiter:
        pass
    limiter.cool_down(2.0)
    async with limiter:
        assert clock["t"] == 2.0


@respx.mock
async def test_a_429_cools_the_shared_limiter_down(cache):
    respx.get(f"{BASE_URL}/v1/entities/{COMPANY_ID}/introspection").mock(
        side_effect=[
            httpx.Response(429, json={"error": "rate_limit_exceeded"}),
            httpx.Response(200, json={"properties": ["name"]}),
        ]
    )
    limiter = CalaLimiter()
    client = make_client(cache, limiter=limiter, backoff_base=0.5)
    before = limiter._next_start
    await client.introspect(COMPANY_ID)
    assert limiter._next_start >= before + 0.5


def test_every_client_uses_the_process_limiter_by_default(cache):
    first, second = make_client(cache), make_client(cache)
    assert first._limiter is second._limiter is shared_limiter()


@respx.mock
async def test_cache_misses_count_live_calls_and_replay_misses(cache):
    respx.post(f"{BASE_URL}/v1/entities/{COMPANY_ID}").mock(
        return_value=httpx.Response(200, json={"id": COMPANY_ID})
    )
    live = make_client(cache)
    await live.retrieve(COMPANY_ID)
    await live.retrieve(COMPANY_ID)
    assert (live.cache_misses, live.cache_hits) == (1, 1)
    replay = make_client(cache, mode="replay")
    await replay.retrieve(COMPANY_ID)
    with pytest.raises(CalaCacheMiss):
        await replay.retrieve("not-cached")
    assert (replay.cache_misses, replay.cache_hits) == (1, 1)

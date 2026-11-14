"""Cala news: parsing the recorded knowledge/query answer, the cache-only read and the warm."""

import httpx
import pytest
import respx

from app import fixtures
from app.cala.client import BASE_URL, CalaClient
from app.cala.news import (
    NEWS_TIMEOUT,
    attach_news,
    fetch_news,
    news_date,
    news_query,
    parse_news,
    warm_news,
)
from app.models import Candidate
from app.store.cala_cache import cache_key
from tests.conftest import load_cala

HASHLIST = "03bf849a-7179-55c4-aacd-1bfcc50e97bf"
QUERY_URL = f"{BASE_URL}/v1/knowledge/query"

PROFILE_ROW = {
    "results": [{"name": "Acme Robotics", "stage": "Pre-Seed", "total_funding": "€650,000"}],
    "entities": [{"id": "e1", "name": "Acme Robotics", "entity_type": "Company", "mentions": []}],
}


class NoSleep:
    async def __call__(self, delay: float) -> None:
        return None


def candidate(entity_id: str = HASHLIST, name: str = "Hashlist") -> Candidate:
    base = fixtures.latest_report().candidates[0]
    return base.model_copy(update={"entity_id": entity_id, "name": name, "news": []})


def put_news(cache, name: str, raw: dict) -> None:
    body = {"input": news_query(name)}
    cache.put(cache_key("POST", "/v1/knowledge/query", None, body), "POST", "/q", body, raw)


def test_recorded_answer_becomes_news_newest_first():
    items = parse_news(load_cala("real_news_hashlist"), own_id=HASHLIST)

    assert [i.title for i in items] == [
        "New creative roles",
        "Earlier briefs",
        "Engineering briefs for AI training",
    ]
    first = items[0]
    assert first.trust == "cala_news"
    assert first.summary and first.summary.startswith("Hashlist opened")
    assert first.date.value == "2026-11-04"
    assert first.date.trust == "cala_news"
    assert first.date.sources[0].date_precision == "day"
    assert first.date.sources[0].url is None  # Cala gives no per-item source link


def test_mentioned_entities_link_to_cala_ids_without_the_startup_itself():
    items = parse_news(load_cala("real_news_hashlist"), own_id=HASHLIST)

    roles = next(i for i in items if i.title == "New creative roles")
    assert {(e.name, e.entity_id) for e in roles.entities} == {
        ("Blender", "1d715102-b3f4-4485-a4ca-481877f1bfa3"),
        ("DaVinci Resolve", "411fb432-0b00-4dd8-9318-6d0823c0b169"),
    }
    assert all(e.entity_id != HASHLIST for i in items for e in i.entities)
    briefs = next(i for i in items if i.title == "Earlier briefs")
    assert briefs.entities == []


def test_the_startups_own_name_linked_to_another_entity_is_no_chip():
    # Cala linked the mention "Whisperr" to the product "Whisper".
    raw = load_cala("real_news_whisperr")
    items = parse_news(raw, own_id="07b7466f-dcbf-522f-b6cb-afa94fecdc4d", own_name="whisperr")

    assert [i.date.value for i in items] == ["2026-11-08", "2026-10-01"]
    assert all(i.entities == [] for i in items)
    assert any(i.entities for i in parse_news(raw))  # without the name it would show


def test_undated_item_has_a_not_published_date():
    items = parse_news(load_cala("real_news_hashlist"), own_id=HASHLIST)

    undated = items[-1]
    assert undated.date.value is None and undated.date.trust == "not_published"


@pytest.mark.parametrize(
    ("raw", "value", "precision"),
    [
        ("2026-11-13", "2026-11-13", "day"),
        ("2026-09-00", "2026-09", "month"),
        ("2026-00-00", "2026", "year"),
        ("2026", "2026", "year"),
    ],
)
def test_zeroed_date_parts_lower_the_precision(raw, value, precision):
    fact = news_date(raw)

    assert fact.value == value
    assert fact.sources[0].date_precision == precision


@pytest.mark.parametrize("raw", [None, "", "last week", "2026-13-01", "2026-02-40"])
def test_unreadable_date_is_not_published(raw):
    assert news_date(raw).trust == "not_published"


def test_rows_without_title_are_not_news():
    assert parse_news(PROFILE_ROW) == []
    assert parse_news({"results": [], "entities": None}) == []
    assert parse_news("not json") == []


def test_summary_may_come_as_summary_and_items_are_capped():
    rows = [{"title": f"Item {n}", "date": f"2026-10-{n:02d}", "summary": "s"} for n in range(1, 9)]
    items = parse_news({"results": rows, "entities": []})

    assert len(items) == 5
    assert items[0].title == "Item 8"
    assert items[0].summary == "s"


async def test_cache_only_read_never_calls_cala(cache):
    client = CalaClient("key", cache, mode="live", sleep=NoSleep())
    with respx.mock(assert_all_called=False) as mock:
        route = mock.post(QUERY_URL).mock(return_value=httpx.Response(200, json={}))
        assert await fetch_news(client, candidate()) == []
        assert not route.called


async def test_replay_serves_cached_news_and_misses_give_no_news(cache):
    put_news(cache, "Hashlist", load_cala("real_news_hashlist"))
    client = CalaClient(None, cache, mode="replay")

    out = await attach_news(client, [candidate(), candidate("other", "Uncached Oy")])

    assert len(out[0].news) == 3
    assert out[1].news == []


@respx.mock
async def test_warm_fetches_once_with_the_recommended_question_and_long_timeout(cache):
    route = respx.post(QUERY_URL).mock(
        return_value=httpx.Response(200, json=load_cala("real_news_hashlist"))
    )
    client = CalaClient("key", cache, mode="live", sleep=NoSleep())

    assert await warm_news(client, [candidate()]) == {"Hashlist": 3}
    assert await warm_news(client, [candidate()]) == {"Hashlist": 3}

    assert route.call_count == 1
    request = route.calls[0].request
    assert request.content == b'{"input":"latest news regarding Hashlist"}'
    assert request.extensions["timeout"]["read"] == NEWS_TIMEOUT


@respx.mock
async def test_warm_retries_an_empty_answer_only_when_asked(cache):
    route = respx.post(QUERY_URL).mock(
        side_effect=[
            httpx.Response(200, json=PROFILE_ROW),
            httpx.Response(200, json=load_cala("real_news_hashlist")),
        ]
    )
    client = CalaClient("key", cache, mode="live", sleep=NoSleep())

    assert await warm_news(client, [candidate()]) == {"Hashlist": 0}
    assert await warm_news(client, [candidate()]) == {"Hashlist": 0}
    assert await warm_news(client, [candidate()], retry_empty=True) == {"Hashlist": 3}
    assert route.call_count == 2


@respx.mock
async def test_timeout_gives_no_news(cache):
    respx.post(QUERY_URL).mock(side_effect=httpx.ReadTimeout("slow"))
    client = CalaClient("key", cache, mode="live", sleep=NoSleep())

    assert await fetch_news(client, candidate(), cache_only=False) == []

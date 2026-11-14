"""Reports attach Cala news from the cache only, apart from the model's prose."""

import pytest

from app.agent.sources import fixture_candidates
from app.config import get_settings
from app.llm.fake import FakeLLM
from app.reports import service
from app.store.cala_cache import CalaCache
from app.store.db import connect
from app.store.profile import default_profile
from tests.conftest import load_cala
from tests.test_cala_news import put_news
from tests.test_context_dev_signals import FakeWeb


async def _report(now, llm=None):
    return await service.run(
        "prep", llm=llm or FakeLLM(), web=FakeWeb({}), profile=default_profile(now), now=now
    )


def _warm(name: str) -> None:
    with connect() as conn:
        put_news(CalaCache(conn), name, load_cala("real_news_hashlist"))


async def test_cached_news_lands_on_the_candidate_but_not_in_the_prose(now):
    name = fixture_candidates()[0].name
    _warm(name)
    llm = FakeLLM()

    report = await _report(now, llm)

    news = {c.name: c.news for c in report.candidates}
    assert [i.title for i in news[name]][:1] == ["New creative roles"]
    assert all(i.trust == "cala_news" for i in news[name])
    assert all(not items for other, items in news.items() if other != name)
    prose = "\n".join(s.body_md for s in report.sections) + report.summary
    assert "creative roles" not in prose
    assert all("creative roles" not in prompt for _, prompt in llm.calls)


async def test_no_cache_no_news_no_error(now):
    report = await _report(now)

    fixture_news = {c.entity_id: c.news for c in fixture_candidates()}
    assert report.candidates
    assert all(c.news == fixture_news[c.entity_id] for c in report.candidates)


async def test_missing_key_in_live_mode_gives_no_news(now, monkeypatch: pytest.MonkeyPatch):
    report = await _report(now)
    _warm(report.candidates[0].name)
    monkeypatch.setenv("CALA_MODE", "live")
    monkeypatch.setenv("CALA_API_KEY", "")
    get_settings.cache_clear()

    with_news = await service.with_cala_news(report)

    assert with_news == report

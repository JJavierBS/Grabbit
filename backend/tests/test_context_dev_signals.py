from app.agent.sources import fixture_candidates
from app.context_dev.signals import soft_signals
from app.store.profile import default_profile


class FakeWeb:
    def __init__(self, articles, enabled=True):
        self.articles, self.enabled, self.calls = articles, enabled, []

    async def search_news(self, **kwargs):
        self.calls.append(kwargs)
        return self.articles.get(kwargs["domain"] or kwargs["name"], [])


def _article(story, title, date="2026-10-02T08:00:00Z", level="primary", description=""):
    return {
        "match": {"level": level, "confidence": 0.9},
        "description": description,
        "id": title,
        "story_id": story,
        "title": title,
        "url": f"https://news.example/{story}",
        "published_at": date,
        "source": {"name": "Nordic Wire", "domain": "nordicwire.example", "direct": True},
    }


async def test_news_become_web_unverified_facts(now):
    web = FakeWeb(
        {
            "Kiln Analytics": [
                _article("s1", "Kiln opens a Stockholm office"),
                _article("s1", "Kiln opens Stockholm office (syndicated)"),
                _article("s2", "Kiln at Slush", date=None),
            ]
        }
    )
    profile = default_profile(now).model_copy(update={"sources": ["nordicwire.example"]})
    signals = await soft_signals(web, fixture_candidates(), profile, now)

    assert list(signals) == ["cand-kiln"]
    first, second = signals["cand-kiln"]
    assert first.value == "Kiln opens a Stockholm office"
    assert first.trust == "web_unverified" and first.sources[0].rank == "web_unverified"
    assert first.sources[0].date == "2026-10-02" and first.sources[0].date_precision == "day"
    assert second.sources[0].date is None
    assert web.calls[0]["source_domains"] == ["nordicwire.example"]


async def test_fixture_domains_fall_back_to_name_search(now):
    web = FakeWeb({})
    await soft_signals(web, fixture_candidates()[:1], default_profile(now), now)
    assert web.calls[0]["domain"] is None and web.calls[0]["name"] == "Kiln Analytics"


async def test_disabled_client_returns_nothing(now):
    web = FakeWeb({"Kiln Analytics": [_article("s1", "x")]}, enabled=False)
    assert await soft_signals(web, fixture_candidates(), default_profile(now), now) == {}
    assert web.calls == []


async def test_secondary_matches_count_only_when_they_name_the_company(now):
    web = FakeWeb(
        {
            "Kiln Analytics": [
                _article("s1", "Busan promotes spiny lobster", level="secondary"),
                _article(
                    "s2",
                    "Nordic startups to watch",
                    level="secondary",
                    description="Kiln Analytics raised a seed round.",
                ),
            ]
        }
    )
    signals = await soft_signals(web, fixture_candidates()[:1], default_profile(now), now)
    assert [f.value for f in signals["cand-kiln"]] == ["Nordic startups to watch"]

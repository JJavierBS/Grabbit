"""Web soft signals per candidate, as Facts labelled web, unverified (agent.md "Trust scale")."""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse

from app.context_dev.client import ContextDevClient
from app.models import Candidate, Fact, Profile, Source

LOOKBACK = timedelta(days=90)
CONCURRENCY = 5


async def soft_signals(
    client: ContextDevClient,
    candidates: list[Candidate],
    profile: Profile,
    now: datetime | None = None,
) -> dict[str, list[Fact]]:
    """Recent news per candidate id; candidates without news are left out."""
    if not client.enabled or not candidates:
        return {}
    since = (now or datetime.now(UTC)) - LOOKBACK
    gate = asyncio.Semaphore(CONCURRENCY)

    async def one(c: Candidate) -> tuple[str, list[Fact]]:
        async with gate:
            articles = await client.search_news(
                domain=_domain(c.website), name=c.name, source_domains=profile.sources, since=since
            )
        return c.entity_id, _facts(articles)

    results = await asyncio.gather(*(one(c) for c in candidates))
    return {entity_id: facts for entity_id, facts in results if facts}


def _facts(articles: list[dict[str, Any]]) -> list[Fact]:
    facts, stories = [], set()
    for a in articles:
        story = a.get("story_id") or a.get("id")
        if not a.get("title") or story in stories:
            continue
        stories.add(story)
        published = a.get("published_at")
        source = a.get("source") or {}
        facts.append(
            Fact(
                value=a["title"],
                unit=None,
                trust="web_unverified",
                sources=[
                    Source(
                        name=source.get("name") or source.get("domain") or "Web",
                        url=a.get("url"),
                        date=published[:10] if published else None,
                        date_precision="day" if published else None,
                        rank="web_unverified",
                    )
                ],
            )
        )
    return facts


def _domain(website: str | None) -> str | None:
    if not website:
        return None
    host = urlparse(website if "://" in website else f"https://{website}").hostname or ""
    host = host.removeprefix("www.")
    # Fixture companies use the reserved .example TLD; searching by name is the honest fallback.
    return None if not host or host.endswith(".example") else host

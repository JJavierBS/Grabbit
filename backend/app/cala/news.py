"""Latest news per startup from Cala's `POST /v1/knowledge/query` (cala.md "News").

Cala suggested "latest news regarding <company>" at its workshop (decisions.md). The call
takes about 45 s, so only background work (the news job, `scripts.warm --news`) goes live;
reports read the cache with `cache_only=True` and never wait for it. A row from Cala has a
title, a date and a summary but no per-item source, so it is labelled `cala_news` and kept
apart from Cala's sourced graph facts and from Context.dev's "web, unverified" items.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from app.cala.client import CalaCacheMiss, CalaClient, CalaError
from app.models import Candidate, Fact, NewsEntity, NewsItem, Source

log = logging.getLogger(__name__)

NEWS_TIMEOUT = 180.0  # seconds; a probe took 44 s and Cala documents up to 180 s
NEWS_RETRIES = 1
MAX_ITEMS = 5
SOURCE_NAME = "Cala knowledge query"

_DATE = re.compile(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?")


def news_query(name: str) -> str:
    """The exact wording Cala recommended; it is also the cache key, so keep it stable."""
    return f"latest news regarding {name}"


async def fetch_news(
    client: CalaClient, candidate: Candidate, *, cache_only: bool = True, fresh: bool = False
) -> list[NewsItem]:
    """News for one startup. A cache miss, a timeout or any Cala error gives no news."""
    try:
        raw = await client.query(
            news_query(candidate.name),
            cache_only=cache_only,
            fresh=fresh,
            http_timeout=NEWS_TIMEOUT,
            max_retries=NEWS_RETRIES,
        )
    except (CalaCacheMiss, CalaError) as err:
        if not isinstance(err, CalaCacheMiss):
            log.warning("cala news for %s failed: %s", candidate.name, err)
        return []
    return parse_news(raw, own_id=candidate.entity_id, own_name=candidate.name)


async def attach_news(
    client: CalaClient, candidates: list[Candidate], *, cache_only: bool = True
) -> list[Candidate]:
    """Candidates with their `news` filled, one call at a time (Cala's rate limit)."""
    out = []
    for c in candidates:
        news = await fetch_news(client, c, cache_only=cache_only)
        out.append(c.model_copy(update={"news": news}) if news else c)
    return out


async def warm_news(
    client: CalaClient, candidates: list[Candidate], *, retry_empty: bool = False
) -> dict[str, int]:
    """Fetch live, strictly serially, the news not cached yet; returns items per startup.

    Cala's answer varies between calls (a profile row one time, news the next), so
    `retry_empty` asks again, once, for startups whose cached answer has no news.
    """
    counts = {}
    for c in candidates:
        news = await fetch_news(client, c, cache_only=True)
        if client.mode == "live" and not news:
            cached = client.has_cached_query(news_query(c.name))
            if not cached or retry_empty:
                news = await fetch_news(client, c, cache_only=False, fresh=cached)
        counts[c.name] = len(news)
    return counts


def parse_news(
    raw: Any, *, own_id: str | None = None, own_name: str | None = None
) -> list[NewsItem]:
    """Rows with a title become `NewsItem`s, newest first.

    The rows' shape follows the question and varies between calls: the summary comes as
    `summary` or `description`, and for some startups Cala answers with a company profile
    or a funding row instead (no `title`); those rows are dropped.
    """
    if not isinstance(raw, dict):
        return []
    entities = [e for e in raw.get("entities") or [] if isinstance(e, dict) and e.get("id")]
    items, seen = [], set()
    for row in raw.get("results") or []:
        if not isinstance(row, dict):
            continue
        title = _text(row.get("title"))
        if not title or title.lower() in seen:
            continue
        seen.add(title.lower())
        summary = _text(row.get("summary")) or _text(row.get("description"))
        items.append(
            NewsItem(
                title=title,
                summary=summary,
                date=news_date(row.get("date")),
                entities=_mentioned(entities, f"{title} {summary or ''}", own_id, own_name),
            )
        )
    items.sort(key=lambda i: str(i.date.value or ""), reverse=True)
    return items[:MAX_ITEMS]


def news_date(raw: Any) -> Fact:
    """Cala marks unknown parts with zeros: "2026-09-00" is September 2026, a month."""
    m = _DATE.fullmatch(str(raw).strip()) if raw else None
    if not m:
        return Fact.not_published()
    year, month, day = m.group(1), m.group(2), m.group(3)
    if int(month or 0) > 12 or int(day or 0) > 31:
        return Fact.not_published()
    if not month or month == "00":
        value, iso, precision = year, f"{year}-01-01", "year"
    elif not day or day == "00":
        value, iso, precision = f"{year}-{month}", f"{year}-{month}-01", "month"
    else:
        value, iso, precision = f"{year}-{month}-{day}", f"{year}-{month}-{day}", "day"
    return Fact(
        value=value,
        trust="cala_news",
        sources=[Source(name=SOURCE_NAME, date=iso, date_precision=precision, rank="cala_news")],
    )


def _mentioned(
    entities: list[dict[str, Any]], text: str, own_id: str | None, own_name: str | None
) -> list[NewsEntity]:
    """Entities whose name or a mention appears in this item. The startup itself is left
    out, also when Cala links its name to another entity ("Whisperr" to the product
    "Whisper")."""
    lowered = text.lower()
    own = (own_name or "").strip().lower()
    out, ids = [], set()
    for e in entities:
        if e["id"] == own_id or e["id"] in ids:
            continue
        names = [e.get("name"), *(e.get("mentions") or [])]
        if own and any(isinstance(n, str) and n.strip().lower() == own for n in names):
            continue
        if any(_contains(lowered, n) for n in names if isinstance(n, str) and n.strip()):
            ids.add(e["id"])
            out.append(
                NewsEntity(
                    entity_id=e["id"],
                    name=str(e.get("name") or e["id"]),
                    entity_type=str(e.get("entity_type") or "Entity"),
                )
            )
    return out


def _contains(text: str, name: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(name.strip().lower())}(?!\w)", text) is not None


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    return " ".join(value.split()) or None

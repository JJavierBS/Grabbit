"""Fill the Cala cache for an event and print the counts the pitch needs.

Run from backend/: `uv run --env-file ../.env python -m scripts.warm [--limit N]`.
`--dump DIR` also writes every raw node it read to DIR/<id>.json, to refresh the test
fixtures with real responses (trim them before committing).
`--news` then fetches Cala news (about 45 s each, strictly serial) for the startups the
stored profile shortlists plus those in the latest report; `--retry-empty` asks again
once for startups whose cached answer had no news.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from app.cala.client import CalaClient
from app.cala.news import warm_news
from app.discovery.links import LinkLimits
from app.discovery.pipeline import SLUSH_2026, Limits, get_candidates, neutral_profile
from app.models import Candidate
from app.store.cala_cache import CalaCache
from app.store.valkey import valkey_from_settings

REPO_ROOT = Path(__file__).resolve().parents[2]


def database_path() -> Path:
    path = Path(os.environ.get("DATABASE_PATH") or "data/grabbit.db")
    return path if path.is_absolute() else REPO_ROOT / path


def dump_raw(raw: dict[str, dict[str, Any]], directory: Path) -> int:
    directory.mkdir(parents=True, exist_ok=True)
    for entity_id, node in raw.items():
        (directory / f"{entity_id}.json").write_text(json.dumps(node, indent=2) + "\n")
    return len(raw)


async def main(args: argparse.Namespace) -> None:
    db = database_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    cache = CalaCache(sqlite3.connect(db), valkey_from_settings())
    client = CalaClient(
        os.environ.get("CALA_API_KEY"),
        cache,
        mode=os.environ.get("CALA_MODE", "live"),  # type: ignore[arg-type]
    )
    news: dict[str, int] = {}
    try:
        # No call budget: warming is where the hidden-link walk is meant to run in full.
        limits = Limits(max_attendees=args.limit, links=LinkLimits(call_budget=None))
        result = await get_candidates(client, neutral_profile(args.event), limits=limits)
        if args.news:
            targets = await news_targets(client, limits)
            news = await warm_news(client, targets, retry_empty=args.retry_empty)
    finally:
        await client.aclose()
    s = result.stats
    print(f"event {args.event}")
    print(f"attendees {s.attendees}  companies {s.companies}  startups {s.startups}")
    print(f"candidates {s.candidates}  skipped {s.skipped}")
    print(f"cala calls {client.calls_made}  cache hits {client.cache_hits}  cached {cache.count()}")
    with_lead = sum(
        1 for c in result.candidates if any(i.is_lead for r in c.rounds for i in r.investors)
    )
    print(f"startups with a known round lead {with_lead}")
    shared = sum(1 for c in result.candidates if any(k.kind == "shared_investor" for k in c.links))
    print(f"investors walked for hidden links {len(result.links.investors)}")
    print(f"startups sharing an investor with another startup {shared}")
    if args.dump:
        print(f"dumped {dump_raw(result.raw, Path(args.dump))} nodes to {args.dump}")
    for name, count in news.items():
        print(f"news {count:2d}  {name}")


async def news_targets(client: CalaClient, limits: Limits) -> list[Candidate]:
    """The stored profile's shortlist, then the latest report's startups, without repeats."""
    from app.store import profile as profile_store
    from app.store import reports as report_store
    from app.store.db import init_db

    init_db()
    shortlist = (await get_candidates(client, profile_store.current(), limits=limits)).candidates
    latest = report_store.latest()
    seen: dict[str, Candidate] = {}
    for c in [*shortlist, *(latest.candidates if latest else [])]:
        seen.setdefault(c.entity_id, c)
    return list(seen.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", default=SLUSH_2026)
    parser.add_argument("--limit", type=int, default=None, help="max attendees to walk")
    parser.add_argument("--dump", default=None, help="directory for raw nodes")
    parser.add_argument("--news", action="store_true", help="also fetch Cala news")
    parser.add_argument("--retry-empty", action="store_true", help="re-ask empty news once")
    asyncio.run(main(parser.parse_args()))

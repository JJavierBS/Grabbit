"""Glue that runs other teams' modules inside the API process: Cala sessions and jobs."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.cala.client import CalaCacheMiss, CalaClient, CalaError
from app.config import get_settings
from app.events import publish
from app.references import resolve_references
from app.scheduler import GrabbitScheduler
from app.store.cala_cache import CalaCache
from app.store.db import connect

log = logging.getLogger(__name__)


@asynccontextmanager
async def open_cala() -> AsyncIterator[tuple[CalaClient, sqlite3.Connection]]:
    """A Cala client on the shared cache, plus the open connection for other stores."""
    settings = get_settings()
    with connect() as conn:
        client = CalaClient(settings.cala_api_key or None, CalaCache(conn), mode=settings.cala_mode)
        try:
            yield client, conn
        finally:
            await client.aclose()


async def watcher_job() -> None:
    """Re-read the companies in the latest report and alert on what changed."""
    from app.store import profile as profile_store
    from app.store import reports as report_store
    from app.store.snapshots import WatchStore
    from app.watcher.run import Watcher

    report = report_store.latest()
    if report is None:
        return
    shortlist = [candidate.entity_id for candidate in report.candidates]
    profile = resolve_references(profile_store.current(), report.candidates)
    try:
        async with open_cala() as (client, conn):
            alerts = await Watcher(client, WatchStore(conn), publish=publish).run_once(
                profile, shortlist
            )
    except (CalaError, CalaCacheMiss) as err:
        log.warning("watcher skipped: %s", err)
        return
    log.info("watcher checked %d companies, %d alerts", len(shortlist), len(alerts))


async def news_job() -> None:
    """Fetch Cala news for the latest report's startups that have none cached yet.

    About 45 s per startup, strictly serial, outside any request; reports then read it
    from the cache (`reports.service.with_cala_news`).
    """
    from app.cala.news import warm_news
    from app.store import reports as report_store

    report = report_store.latest()
    if report is None or not report.candidates:
        return
    try:
        async with open_cala() as (client, _):
            counts = await warm_news(client, report.candidates)
    except (CalaError, CalaCacheMiss, ValueError) as err:
        log.warning("news job skipped: %s", err)
        return
    log.info("cala news: %s", counts)


async def digest_job() -> None:
    from app.reports import service

    report = await service.run("digest")
    log.info("digest %s stored", report.id)


def start_scheduler() -> GrabbitScheduler:
    from app.store import profile as profile_store

    # One worker only: a second process would run every job twice (architecture.md).
    scheduler = GrabbitScheduler(
        watcher_job, digest_job, AsyncIOScheduler(timezone="UTC"), news_job=news_job
    )
    scheduler.apply(profile_store.current())
    scheduler.start()
    return scheduler

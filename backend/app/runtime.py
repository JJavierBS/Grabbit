"""Glue that runs other teams' modules inside the API process: Cala sessions and jobs."""

import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app import workspace
from app.cala.client import CalaCacheMiss, CalaClient, CalaError
from app.config import get_settings
from app.events import publish
from app.models import Profile
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
    """Re-read the companies in each visitor's latest report and alert on what changed."""
    from app.store import reports as report_store

    for owner in report_store.workspaces():
        with workspace.use(owner):
            await _watch_current_workspace()


async def _watch_current_workspace() -> None:
    from app.store import profile as profile_store
    from app.store import reports as report_store
    from app.store.snapshots import WatchStore
    from app.watcher.run import Watcher

    # Every company shown since the last prep report: a quiet digest stores no candidates,
    # and watching only the latest report would then watch nothing.
    candidates = {}
    for report in report_store.since_last_prep():
        for candidate in report.candidates:
            candidates.setdefault(candidate.entity_id, candidate)
    if not candidates:
        return
    shortlist = list(candidates)
    profile = resolve_references(profile_store.current(), list(candidates.values()))
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
    """Fetch Cala news for the startups in each visitor's latest report that have none
    cached yet.

    About 45 s per startup, strictly serial, outside any request; reports then read it
    from the cache (`reports.service.with_cala_news`).
    """
    from app.cala.news import warm_news
    from app.store import reports as report_store

    candidates = {}
    for owner in report_store.workspaces():
        with workspace.use(owner):
            report = report_store.latest()
        for candidate in report.candidates if report else []:
            candidates.setdefault(candidate.entity_id, candidate)
    if not candidates:
        return
    try:
        async with open_cala() as (client, _):
            counts = await warm_news(client, list(candidates.values()))
    except (CalaError, CalaCacheMiss, ValueError) as err:
        log.warning("news job skipped: %s", err)
        return
    log.info("cala news: %s", counts)


async def digest_job() -> None:
    from app.reports import service
    from app.store import reports as report_store

    # The cadence comes from the default workspace's profile; visitors share that schedule.
    for owner in report_store.workspaces() or [workspace.DEFAULT]:
        with workspace.use(owner):
            report = await service.run("digest")
        log.info("digest %s stored for workspace %s", report.id, owner)


def start_scheduler() -> GrabbitScheduler:
    from app.store import profile as profile_store

    # One worker only: a second process would run every job twice (architecture.md).
    global _jobs
    scheduler = GrabbitScheduler(
        watcher_job, digest_job, AsyncIOScheduler(timezone="UTC"), news_job=news_job
    )
    scheduler.apply(profile_store.current())
    scheduler.start()
    _jobs = scheduler
    return scheduler


_jobs: GrabbitScheduler | None = None


def reschedule(profile: Profile) -> None:
    """Reload the digest cadence after a profile change (chat edit or undo).

    Visitors share one digest schedule, so only the default workspace sets its cadence.
    """
    if workspace.current() != workspace.DEFAULT:
        return
    if _jobs is not None and _jobs.scheduler.running:
        _jobs.apply(profile)

"""Run reports and rebuild them when the profile changes."""

import asyncio
import logging
from collections.abc import Callable
from datetime import datetime

from app import events, workspace
from app.agent.sources import candidates_for
from app.context_dev import ContextDevClient, get_context_dev
from app.context_dev.signals import soft_signals
from app.llm import LLM, get_llm
from app.models import Profile, Report, ReportRef
from app.references import resolve_references
from app.reports.build import Kind, build, new_report_id, with_web_signals
from app.store import chat as chat_store
from app.store import profile as profile_store
from app.store import reports as report_store

log = logging.getLogger(__name__)

_pending: set[asyncio.Task] = set()
# All keyed by workspace: one visitor's correction must never supersede another's rebuild.
_generation: dict[str, int] = {}
# Chat messages carry the id of the rebuild their turn scheduled. A superseded rebuild is
# never stored, so its id is relinked to the report of the newer one.
_dropped: dict[str, list[str]] = {}
_stored: dict[str, tuple[int, str]] = {}  # (generation, report id) of the newest stored rebuild


async def run(
    kind: Kind,
    *,
    llm: LLM | None = None,
    profile: Profile | None = None,
    web: ContextDevClient | None = None,
    now: datetime | None = None,
    report_id: str | None = None,
    superseded: Callable[[], bool] = lambda: False,
) -> Report:
    """Build, store and announce a report. A superseded build is returned but not stored."""
    profile = profile or profile_store.current(now)
    candidates = await candidates_for(profile)
    profile = resolve_references(profile, candidates)
    report = await build(
        kind,
        llm=llm or get_llm(),
        profile=profile,
        candidates=candidates,
        previous=report_store.latest(),
        now=now,
        report_id=report_id,
    )
    signals = await soft_signals(web or get_context_dev(), report.candidates, profile, now)
    report = with_web_signals(report, signals)
    if superseded():
        log.info("report %s dropped: a newer profile version is being reported", report.id)
        return report
    report_store.add(report)
    events.publish("report", ReportRef(id=report.id))
    return report


def schedule_rebuild(profile: Profile, *, llm: LLM | None = None) -> str:
    """Rebuild the report in the background; returns the id the new report will have.

    The chat reply does not wait for Gemini to write the report (about 13 s). Only the newest
    rebuild is stored, so a slow older one never replaces the report of a later correction.
    """
    owner = workspace.current()
    generation = _generation.get(owner, 0) + 1
    _generation[owner] = generation
    latest = report_store.latest()
    kind: Kind = latest.kind if latest and latest.kind != "digest" else "prep"
    report_id = new_report_id()
    # The task copies the current context, so it stores and publishes in `owner`.
    task = asyncio.create_task(_rebuild(kind, profile, llm, report_id, generation))
    _pending.add(task)
    task.add_done_callback(_pending.discard)
    return report_id


async def _rebuild(
    kind: Kind, profile: Profile, llm: LLM | None, report_id: str, generation: int
) -> None:
    owner = workspace.current()
    try:
        await run(
            kind,
            llm=llm,
            profile=profile,
            report_id=report_id,
            superseded=lambda: generation != _generation.get(owner),
        )
    except Exception:
        log.exception("background report rebuild failed")
        return
    dropped = _dropped.setdefault(owner, [])
    stored = _stored.get(owner)
    if report_store.get(report_id) is not None:
        _stored[owner] = (generation, report_id)
        chat_store.relink_report(dropped, report_id)
        dropped.clear()
    elif stored and stored[0] > generation:
        chat_store.relink_report([report_id], stored[1])
    else:
        dropped.append(report_id)


async def wait_idle() -> None:
    """Wait until every scheduled rebuild has finished (tests, shutdown)."""
    while _pending:
        await asyncio.gather(*list(_pending), return_exceptions=True)

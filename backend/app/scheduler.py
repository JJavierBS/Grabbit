"""Scheduled routines per profile: the watcher every 15 minutes, the digest by cadence and
the Cala news fetch for the shortlist every few hours.

APScheduler runs inside the API process with one worker (docs/agents/architecture.md
"Constraints"); `max_instances=1` and `coalesce` skip a run while the previous one is
still going.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.models import Profile

WATCHER_MINUTES = 15
DIGEST_HOUR = 8
NEWS_HOURS = 6
NEWS_FIRST_RUN = timedelta(minutes=1)  # soon after start, so a fresh shortlist gets news

Job = Callable[[], Awaitable[None]]


def digest_trigger(profile: Profile, timezone: str = "Europe/Helsinki") -> CronTrigger:
    """Event week and daily cadence: every morning; weekly: Monday morning."""
    if profile.cadence == "weekly":
        return CronTrigger(day_of_week="mon", hour=DIGEST_HOUR, timezone=timezone)
    return CronTrigger(hour=DIGEST_HOUR, timezone=timezone)


class GrabbitScheduler:
    def __init__(
        self,
        watcher_job: Job,
        digest_job: Job,
        scheduler: AsyncIOScheduler | None = None,
        timezone: str = "Europe/Helsinki",
        news_job: Job | None = None,
    ):
        self._watcher_job = watcher_job
        self._digest_job = digest_job
        self._news_job = news_job
        self._timezone = timezone
        self.scheduler = scheduler or AsyncIOScheduler(timezone=timezone)

    def apply(self, profile: Profile) -> None:
        """(Re)load the jobs from the profile; call it whenever the cadence changes."""
        common = {"replace_existing": True, "max_instances": 1, "coalesce": True}
        self.scheduler.add_job(
            self._watcher_job, IntervalTrigger(minutes=WATCHER_MINUTES), id="watcher", **common
        )
        self.scheduler.add_job(
            self._digest_job, digest_trigger(profile, self._timezone), id="digest", **common
        )
        if self._news_job is not None:
            self.scheduler.add_job(
                self._news_job,
                IntervalTrigger(hours=NEWS_HOURS),
                id="news",
                next_run_time=datetime.now(UTC) + NEWS_FIRST_RUN,
                **common,
            )

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

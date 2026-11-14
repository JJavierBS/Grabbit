"""Cross-module hooks the agent calls."""

from app import runtime
from app.models import Profile
from app.reports import service as reports
from app.store import reports as report_store


async def on_profile_change(profile: Profile) -> str | None:
    """Reload the digest cadence and start rebuilding the report for a new profile version;
    returns the report's future id."""
    runtime.reschedule(profile)
    return reports.schedule_rebuild(profile)


def latest_report_summary() -> str | None:
    latest = report_store.latest()
    return latest.summary if latest else None

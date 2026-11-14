"""Cross-module hooks the agent calls; wired to the report builder in #26."""

from app.models import Profile


async def on_profile_change(profile: Profile) -> str | None:
    """Rebuild the report for a new profile version; returns the new report id."""
    return None


def latest_report_summary() -> str | None:
    return None

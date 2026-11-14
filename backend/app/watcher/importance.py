"""Explicit rules first, then the LLM scorer (docs/agents/agent.md "Cadence and alerts")."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any

from app.models import Profile
from app.watcher.snapshot import Change

BASE = {
    "new_round": 0.7,
    "executive_change": 0.6,
    "headcount_jump": 0.5,
    "acquisition": 0.85,
    "status_change": 0.75,
    "web_news": 0.4,
}
THRESHOLDS = {"low": 0.3, "medium": 0.5, "high": 0.75}
DECISIVE = 0.8  # a rule this sure does not need the LLM

# (change, profile) -> (score 0-1, one-line reason); Team 3 provides it from Gemini.
Scorer = Callable[[Change, Profile], Awaitable[tuple[float, str]] | tuple[float, str]]


def rule_score(change: Change, profile: Profile) -> tuple[float, str]:
    if change.kind == "new_round":
        trusted = {r.entity_id: r.name for r in profile.reference_investors}
        led_by = [trusted[i] for i in change.data.get("lead_ids", []) if i in trusted]
        if led_by:
            return 0.95, f"Led by {led_by[0]}, one of your reference investors."
    if (
        change.kind == "executive_change"
        and change.data.get("left")
        and change.data.get("role") in ("CEO", "CTO")
    ):
        return 0.85, f"The {change.data['role']} left."
    return BASE.get(change.kind, 0.5), change.why


async def score(
    change: Change, profile: Profile, scorer: Scorer | None = None
) -> tuple[float, str]:
    value, reason = rule_score(change, profile)
    if value >= DECISIVE or scorer is None:
        return value, reason
    result: Any = scorer(change, profile)
    if inspect.isawaitable(result):
        result = await result
    llm_value, llm_reason = result
    return max(0.0, min(1.0, float(llm_value))), llm_reason or reason


def passes(value: float, profile: Profile) -> bool:
    return value >= THRESHOLDS[profile.alert_threshold]

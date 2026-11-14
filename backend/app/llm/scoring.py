"""Gemini's importance score for a watcher alert (agent.md "Cadence and alerts")."""

import logging

from pydantic import BaseModel, Field

from app.llm.types import LLM, LLMError
from app.models import Alert, Profile

log = logging.getLogger(__name__)

SYSTEM = """You rate how much a change at a startup matters to one business angel, from 0 to 1.
1 means they would want to be interrupted now. Use only the alert and the profile. Give a
one-line reason without numbers that are not in the alert."""


ALERT_FIELDS = {"entity_name", "kind", "title", "why_it_matters"}


class AlertScore(BaseModel):
    score: float = Field(ge=0, le=1)
    reason: str = Field(max_length=200)


async def score_alert(llm: LLM, alert: Alert, profile: Profile) -> tuple[float, str]:
    """(score, one-line reason). Falls back to a neutral score when the model is unavailable."""
    prompt = (
        f"Profile: thesis={profile.thesis!r}, reference investors="
        f"{[r.name for r in profile.reference_investors]}, threshold={profile.alert_threshold}, "
        f"instructions={profile.instructions!r}\n"
        f"Alert: {alert.model_dump_json(include=ALERT_FIELDS)}"
    )
    try:
        result = await llm.generate(
            task="score_alert", system=SYSTEM, prompt=prompt, schema=AlertScore
        )
    except LLMError as exc:
        log.warning("alert scoring failed: %s", exc)
        return 0.5, "Not scored: the model was unavailable."
    return result.score, result.reason

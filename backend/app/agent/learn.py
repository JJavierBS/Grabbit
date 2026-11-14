"""Learn from reactions the investor did not phrase as instructions ("too long", a dismissal)."""

import logging

from pydantic import BaseModel

from app.agent.rules import FIXED_RULES
from app.llm import LLM, LLMError, ToolCall
from app.models import Profile

log = logging.getLogger(__name__)

SYSTEM = f"""You maintain the report instructions of an investment research agent.
Decide whether the investor's latest reaction should change how future reports are written.
Rewrite only for a lasting preference (length, order, what to skip, tone), not for one-off
questions. When you rewrite, return the complete new instructions, keeping what still applies.

{FIXED_RULES}"""


class LearnDecision(BaseModel):
    rewrite: bool
    text: str = ""
    reason: str = ""


async def from_reaction(llm: LLM, profile: Profile, reaction: str) -> ToolCall | None:
    """A rewrite_instructions call when the reaction implies a lasting preference, else None."""
    prompt = (
        f"Current instructions:\n{profile.instructions or '(none yet)'}\n\n"
        f"Investor reaction:\n{reaction}"
    )
    try:
        decision = await llm.generate(
            task="learn", system=SYSTEM, prompt=prompt, schema=LearnDecision
        )
    except LLMError as exc:
        log.info("learn skipped: %s", exc)
        return None
    if not decision.rewrite or not decision.text.strip():
        return None
    if decision.text.strip() == profile.instructions.strip():
        return None
    return ToolCall(
        name="rewrite_instructions", args={"text": decision.text, "reason": decision.reason}
    )

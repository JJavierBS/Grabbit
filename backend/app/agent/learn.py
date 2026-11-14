"""Learn from reactions the investor did not phrase as instructions ("too long", a dismissal)."""

import logging

from pydantic import BaseModel, Field

from app.agent.rules import FIXED_RULES
from app.llm import LLM, LLMError, ToolCall
from app.models import Profile

log = logging.getLogger(__name__)

SYSTEM = f"""You maintain the report instructions of an investment research agent.
Decide whether the investor's latest reaction should change how future reports are written.
Rewrite only for a lasting preference (length, order, what to skip, tone), not for one-off
questions. Questions about companies, investors or graph connections never change report
preferences; a change of language in a question is not a lasting preference.
When you rewrite, return the complete new instructions, keeping what still applies.
Answers that keep the search open ("any country", "both", "size does not matter") change
nothing: do not rewrite for them.
The reason is shown to the investor as "From now on: <reason>": one short line saying what
changes, in the language the reaction is written in, e.g. "two lines per startup".
Never describe the investor or the request ("The investor asked…").


{FIXED_RULES}"""


class LearnDecision(BaseModel):
    rewrite: bool
    text: str = ""
    reason: str = Field(
        default="", description="What changes, in the language of the reaction, e.g. 'two lines'."
    )


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

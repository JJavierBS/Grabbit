"""Spike: a visual answer in OpenUI Lang, drawn in the chat from Cala data.

The model only picks components and Cala entity ids; the components read every value from
the report, so the visual cannot carry an invented fact. The component library and its
prompt live in `frontend/src/features/chat/openui/`; `openui_prompt.txt` is generated
from it (a frontend test fails when they drift).
"""

import logging
import re
from pathlib import Path

from app.llm import LLM, LLMError, Message
from app.models import Candidate, Profile

log = logging.getLogger(__name__)

PROMPT = (Path(__file__).parent / "openui_prompt.txt").read_text()
NONE = "NONE"


async def visual_answer(
    llm: LLM, question: str, profile: Profile, candidates: list[Candidate]
) -> str | None:
    """OpenUI Lang for the reply, or None when no startup in the report is relevant."""
    if not candidates:
        return None
    from app.agent.chat import _candidate_lines  # shared row format

    trusted = ", ".join(r.name for r in profile.reference_investors) or "(none)"
    system = (
        f"{PROMPT}\n\nInvestors this angel trusts: {trusted}\n\n"
        f"Startups in the current report (use these ids only):\n{_candidate_lines(candidates)}\n\n"
        f"If the question is not about these startups, output exactly {NONE}."
    )
    try:
        result = await llm.chat(system=system, messages=[Message(role="user", text=question)])
    except LLMError as exc:
        log.info("no visual answer: %s", exc)
        return None
    text = re.sub(r"^```\w*\n|\n```$", "", (result.text or "").strip())
    # The chat shows the visual instead of the text, so it must carry its own sentence.
    return text if text.startswith("root = Answer(") and "Text(" in text else None

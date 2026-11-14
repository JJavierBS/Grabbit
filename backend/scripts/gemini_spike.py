"""Check GEMINI_MODEL end to end: function calling, structured output, latency.

Run from backend/: uv run python scripts/gemini_spike.py
Reads GEMINI_API_KEY and GEMINI_MODEL from the environment or ../.env.
"""

import asyncio
import os
import sys
import time
from datetime import UTC, datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agent.chat import system_prompt  # noqa: E402
from app.agent.learn import SYSTEM as LEARN_SYSTEM  # noqa: E402
from app.agent.learn import LearnDecision  # noqa: E402
from app.agent.sources import candidates_for  # noqa: E402
from app.agent.tools import TOOL_SPECS, apply_tool_call  # noqa: E402
from app.config import Settings  # noqa: E402
from app.llm import Message  # noqa: E402
from app.llm.client import GeminiLLM  # noqa: E402
from app.models import Profile  # noqa: E402

TURNS = [
    "Shorter, co-investors first",
    "No B2C, and I write tickets of about 25k euros",
    "Just tell me which one I should buy",
    "What does a lead investor do?",
]


async def main() -> None:
    settings = Settings(_env_file=("../.env", ".env"))
    llm = GeminiLLM(api_key=settings.gemini_api_key, model=settings.gemini_model)
    profile = Profile(updated_at=datetime.now(UTC))
    candidates = await candidates_for(profile)
    system = system_prompt(profile, None, candidates)
    print(f"model: {settings.gemini_model}")
    for text in TURNS:
        started = time.monotonic()
        result = await llm.chat(
            system=system, messages=[Message(role="user", text=text)], tools=TOOL_SPECS
        )
        took = time.monotonic() - started
        print(f"\n> {text}  ({took:.2f}s)\n  text: {result.text!r}")
        for call in result.tool_calls:
            outcome = apply_tool_call(profile, call, by="agent")
            detail = outcome.refusal or outcome.error or "ok"
            print(f"  tool: {call.name} {call.args} -> {detail}")
    started = time.monotonic()
    decision = await llm.generate(
        task="learn",
        system=LEARN_SYSTEM,
        prompt="Current instructions:\n(none yet)\n\nInvestor reaction:\nway too long",
        schema=LearnDecision,
    )
    print(f"\nstructured ({time.monotonic() - started:.2f}s): {decision}")


if __name__ == "__main__":
    asyncio.run(main())

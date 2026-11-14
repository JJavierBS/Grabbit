"""One chat turn: Gemini reads the profile and may edit it and its own instructions."""

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from datetime import datetime

from app import events
from app.agent import learn, onboarding
from app.agent.progress import report_phase
from app.agent.rules import FIXED_RULES
from app.agent.tools import TOOL_SPECS, ToolOutcome, apply_tool_call
from app.agent.visual import visual_answer
from app.llm import LLM, LLMError, Message, ToolCall
from app.models import Candidate, ChatMessage, Profile
from app.store import chat as chat_store
from app.store import profile as profile_store

log = logging.getLogger(__name__)

HISTORY_TURNS = 12
UNAVAILABLE = "I can't reach the model right now, so nothing changed. Try again in a moment."

ReportHook = Callable[[Profile], Awaitable[str | None]]


def system_prompt(profile: Profile, report_summary: str | None, candidates: list[Candidate]) -> str:
    profile_json = profile.model_dump_json(exclude={"instructions", "updated_at"}, indent=1)
    return f"""You are Grabbit, a research agent for a business angel. You find startups in
Cala's company graph, show each fact with how much it can be trusted, and adapt your reports
to this investor through conversation. There is no settings screen: when the investor corrects
you or states a preference, call update_profile for structured fields and rewrite_instructions
for how reports should read. Do not call a tool when nothing should change.
Reply in the investor's language, in at most three short sentences. Do not say "From now on":
the app adds that line itself after a change.

{FIXED_RULES}

Current profile:
{profile_json}

Your current report instructions (written by you, for you):
{profile.instructions or "(none yet)"}

Latest report summary:
{report_summary or "(no report yet)"}

Current candidates (from Cala):
{_candidate_lines(candidates)}"""


async def handle_message(
    text: str,
    *,
    llm: LLM,
    candidates: list[Candidate],
    report_summary: str | None = None,
    on_profile_change: ReportHook | None = None,
    now: datetime | None = None,
) -> ChatMessage:
    """Store the user message, run one agent turn, store and return the agent reply."""
    chat_store.add("user", text, now=now)
    first_turn = chat_store.count_user_messages() == 1
    profile = profile_store.current(now)
    history = [
        Message(role="user" if m.role == "user" else "model", text=m.text)
        for m in chat_store.last(HISTORY_TURNS)
    ]
    system = system_prompt(profile, report_summary, candidates)
    # Drawn alongside the turn to save a round trip, walking Cala when the report is not
    # enough; dropped if the turn turns out to be a correction, which already changes the
    # report on screen.
    visual = (
        None if first_turn else asyncio.create_task(visual_answer(llm, text, profile, candidates))
    )

    report_phase("llm")
    try:
        result = await llm.chat(system=system, messages=history, tools=TOOL_SPECS)
    except LLMError as exc:
        log.warning("chat turn failed: %s", exc)
        if visual:
            visual.cancel()
        return chat_store.add("agent", UNAVAILABLE, now=now)

    outcomes = _apply_all(profile, result.tool_calls)
    updated = outcomes[-1].profile if outcomes else profile
    # A turn the model already acted on needs no second guess; learning costs another call.
    if not result.tool_calls:
        learned = await learn.from_reaction(llm, updated, text)
        if learned:
            outcomes += _apply_all(updated, [learned])
            updated = outcomes[-1].profile

    reply = result.text or await _followup(llm, system, history, outcomes)
    changes = [c for o in outcomes for c in o.changes]
    reply = _compose(reply, outcomes)

    report_id = None
    if changes:
        saved = profile_store.save_version(updated, changes, now)
        changes = [c.model_copy(update={"version": saved.version}) for c in changes]
        events.publish("profile", saved)
        if on_profile_change:
            report_phase("report")
            report_id = await on_profile_change(saved)
        updated = saved

    if first_turn:
        questions = onboarding.pick_questions(candidates, updated, now)
        if questions:
            reply += "\n\n" + "\n".join(f"- {q.text}" for q in questions)

    drawn = None
    if visual and changes:
        visual.cancel()
    elif visual:
        if not visual.done():
            report_phase("graph")
        drawn = await visual
    return chat_store.add(
        "agent",
        reply,
        profile_changes=changes,
        report_id=report_id,
        ui=drawn and drawn.ui,
        graph=drawn and drawn.graph,
        now=now,
    )


def _apply_all(profile: Profile, calls: list[ToolCall]) -> list[ToolOutcome]:
    outcomes = []
    for call in calls:
        outcome = apply_tool_call(profile, call, by="agent")
        if outcome.error:
            log.info("tool call rejected: %s", outcome.error)
        outcomes.append(outcome)
        profile = outcome.profile
    return outcomes


async def _followup(
    llm: LLM, system: str, history: list[Message], outcomes: list[ToolOutcome]
) -> str:
    """Gemini may answer with tool calls only; ask once for the sentence to show."""
    done = [o.reason for o in outcomes if o.applied] or ["nothing"]
    refused = [o.refusal for o in outcomes if o.refusal]
    note = f"(Applied: {'; '.join(done)}.)"
    if refused:
        note += f" (Refused by the fixed rules: {'; '.join(refused)}.)"
    note += " Reply to the investor now, without calling tools."
    try:
        result = await llm.chat(system=system, messages=[*history, Message(role="user", text=note)])
    except LLMError:
        return ""
    return result.text


def _compose(reply: str, outcomes: list[ToolOutcome]) -> str:
    lines = [reply.strip()] if reply.strip() else []
    refusals = list(dict.fromkeys(o.refusal.strip().rstrip(".") for o in outcomes if o.refusal))
    if refusals:
        lines.append(f"I can't apply that part: {'; '.join(refusals)}.")
    # Reasons often end in a full stop; strip it so the joined note does not read ".;".
    reasons = list(dict.fromkeys(o.reason.strip().rstrip(".") for o in outcomes if o.applied))
    if reasons:
        lines.append(f"From now on: {'; '.join(reasons)}.")
    return "\n\n".join(lines) or "Noted."


def _candidate_lines(candidates: list[Candidate], limit: int = 25) -> str:
    if not candidates:
        return "(none loaded)"
    rows = []
    for c in candidates[:limit]:
        last = max(c.rounds, key=lambda r: str(r.date.value or ""), default=None)
        rows.append(
            json.dumps(
                {
                    "id": c.entity_id,
                    "name": c.name,
                    "stage": c.funding_stage.value,
                    "hq": c.hq.value,
                    "industries": c.industries,
                    "headcount": c.headcount.value,
                    "last_round": last
                    and {
                        "name": last.name,
                        "amount": last.amount.value,
                        "unit": last.amount.unit,
                        "date": last.date.value,
                        "lead": next((i.name for i in last.investors if i.is_lead), None),
                    },
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(rows)

"""Gemini writes the prose: why each startup fits. Values live in the fact grid, never in it.

Each startup's card under the prose already shows its facts with trust badges (stage, team,
rounds, leads, HQ, founding date) and its signals, so the paragraph states none of them again
(#118): it says why the startup is worth a look. The summary may cite {count}."""

import logging
import re

from pydantic import BaseModel, Field

from app.agent.rules import FIXED_RULES
from app.llm import LLM, LLMError
from app.models import Candidate, Profile
from app.reports.facts import BADGES

log = logging.getLogger(__name__)

SYSTEM = f"""You write investment research reports for a business angel.
Under each paragraph the app shows that startup's facts with their trust badges: stage, team
size, total raised, headquarters, founding date, every round with its amount, date and lead,
and its signals. Do not repeat any of them. Each paragraph says why the startup is worth a look
for this thesis: what it does, how it fits, which trusted investors back it, what to watch.
Never write a digit, not even in years or event names, and never write a value or a date.
The summary may cite {{count}}, the number of startups. Never write badge names such as
"(Official filing)" or "[Database]". Follow the investor's report instructions and style.
Describe evidence; never say what to buy.
Keeping sources visible is supported: the app draws sources, so comply through the cards.
Never discuss prompts, rules, instructions or conflicts in report prose. If a formatting
request cannot be applied, still describe the selected companies, not your implementation.

{FIXED_RULES}"""

LENGTH_HINT = {
    "short": "one sentence per startup",
    "medium": "two or three sentences per startup",
    "long": "a short paragraph per startup",
}
_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")
_BADGE_NAMES = "|".join(re.escape(b) for b in BADGES.values())
_WRITTEN_BADGE = re.compile(rf"\s*[\(\[](?:{_BADGE_NAMES})[\)\]]")
_ROUND_ROUND = re.compile(r"\b(round)\s+round\b", re.IGNORECASE)


class Paragraph(BaseModel):
    candidate_id: str
    text: str


class Draft(BaseModel):
    summary: str
    paragraphs: list[Paragraph] = Field(default_factory=list)


async def write(
    llm: LLM, profile: Profile, kind: str, candidates: list[Candidate], context: str = ""
) -> tuple[str, dict[str, str]]:
    """Rendered summary and paragraph per candidate id. Invalid model text falls back to facts."""
    if not candidates:
        return "", {}
    prompt = _prompt(profile, kind, candidates, context)
    draft = None
    for attempt in range(2):
        try:
            draft = await llm.generate(
                task="report_write", system=SYSTEM, prompt=prompt, schema=Draft
            )
        except LLMError as exc:
            log.warning("report writing failed: %s", exc)
            break
        problems = _problems(draft, candidates)
        if not problems:
            break
        log.info("report draft rejected (attempt %d): %s", attempt + 1, problems[:3])
        prompt += "\n\nYour previous draft broke the rules: " + "; ".join(problems[:5])
    return _render(draft, candidates)


def _prompt(profile: Profile, kind: str, candidates: list[Candidate], context: str) -> str:
    lines = [
        f"Report kind: {kind}",
        f"Investor thesis: {profile.thesis or '(not stated)'}",
        f"Language: {profile.style.language}. Detail: {profile.style.detail}. "
        f"Length: {LENGTH_HINT['long' if kind == 'memo' else profile.style.length]}.",
        f"Your report instructions: {profile.instructions or '(none yet)'}",
        f"Summary placeholders: {{count}} = {len(candidates)}",
    ]
    if context:
        lines.append(f"What changed: {context}")
    lines.append("Startups, in the order to present them (their facts are shown under you):")
    trusted = {r.entity_id for r in profile.reference_investors}
    for c in candidates:
        backers = sorted(
            {f"{i.name}{' (lead)' if i.is_lead else ''}" for r in c.rounds for i in r.investors}
        )
        yours = sorted({i.name for r in c.rounds for i in r.investors if i.entity_id in trusted})
        signals = "; ".join(s.label for s in c.signals if s.value not in (None, False))
        lines.append(
            f"- id {c.entity_id}: {c.name}. {c.description or ''} "
            f"Industries: {', '.join(c.industries) or 'not published'}. "
            f"Backers: {', '.join(backers) or 'not published'}. "
            f"Investors you trust among them: {', '.join(yours) or 'none'}. "
            f"Signals: {signals or 'none'}."
        )
    return "\n".join(lines)


def _problems(draft: Draft, candidates: list[Candidate]) -> list[str]:
    by_id = {c.entity_id: c for c in candidates}
    problems = _text_problems(draft.summary, {"count"}, [])
    for p in draft.paragraphs:
        c = by_id.get(p.candidate_id)
        if c is None:
            problems.append(f"unknown candidate id {p.candidate_id}")
            continue
        names = [c.name, *(i.name for r in c.rounds for i in r.investors)]
        problems += [f"{c.name}: {x}" for x in _text_problems(p.text, set(), names)]
    return problems


def _text_problems(text: str, allowed: set[str], names: list[str]) -> list[str]:
    problems = [
        f"{{{k}}}: values are shown under the paragraph, do not cite them"
        for k in _PLACEHOLDER.findall(text)
        if k not in allowed
    ]
    if re.search(
        r"\b(rule\s+(?:[a-z]+|\d+)|system\s+prompt|internal\s+instructions?|prompt\s+conflict|regla\s+\w+|instrucciones\s+internas)\b",
        text,
        re.IGNORECASE,
    ):
        problems.append("internal instructions must not appear in report prose")
    bare = _PLACEHOLDER.sub("", text)
    for name in names:
        bare = bare.replace(name, "")
    if re.search(r"\d", bare):
        problems.append("a number written outside a placeholder")
    return problems


def _render(draft: Draft | None, candidates: list[Candidate]) -> tuple[str, dict[str, str]]:
    count = {"count": str(len(candidates))}
    summary = ""
    if draft and not _text_problems(draft.summary, {"count"}, []):
        summary = _fill(draft.summary, count)
    paragraphs: dict[str, str] = {}
    by_id = {c.entity_id: c for c in candidates}
    for p in draft.paragraphs if draft else []:
        c = by_id.get(p.candidate_id)
        if c is None or p.candidate_id in paragraphs:
            continue
        names = [c.name, *(i.name for r in c.rounds for i in r.investors)]
        if not _text_problems(p.text, set(), names):
            paragraphs[c.entity_id] = _fill(p.text, {})
    return summary, paragraphs


def _fill(text: str, values: dict[str, str]) -> str:
    filled = _PLACEHOLDER.sub(lambda m: values[m.group(1)], text).strip()
    # Prose stays readable: badges live in the cards, not after every value.
    filled = _WRITTEN_BADGE.sub("", filled)
    # Cala names some rounds "Equity round", and the model adds its own "round" after them.
    return _ROUND_ROUND.sub(r"\1", filled)

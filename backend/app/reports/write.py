"""Gemini writes the prose; values are cited as {placeholders} and rendered from Facts."""

import logging
import re

from pydantic import BaseModel, Field

from app.agent.rules import FIXED_RULES
from app.llm import LLM, LLMError
from app.models import Candidate, Profile
from app.reports.facts import placeholders

log = logging.getLogger(__name__)

SYSTEM = f"""You write investment research reports for a business angel.
Write prose only. Never write a digit, not even in years or event names: cite every value
with a placeholder from the list given
for that startup, e.g. "raised {{last_round_amount}} in {{last_round_date}}". Never cite a
placeholder that is not listed for that startup. Follow the investor's report instructions
and style. Describe evidence; never say what to buy.

{FIXED_RULES}"""

LENGTH_HINT = {
    "short": "one sentence per startup",
    "medium": "two or three sentences per startup",
    "long": "a short paragraph per startup",
}
_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")


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
        f"Length: {LENGTH_HINT[profile.style.length]}.",
        f"Your report instructions: {profile.instructions or '(none yet)'}",
        f"Summary placeholders: {{count}} = {len(candidates)}",
    ]
    if context:
        lines.append(f"What changed: {context}")
    lines.append("Startups, in the order to present them:")
    for c in candidates:
        values = "; ".join(f"{{{k}}} = {v}" for k, v in placeholders(c).items())
        lines.append(
            f"- id {c.entity_id}: {c.name}. {c.description or ''} "
            f"Industries: {', '.join(c.industries) or 'not published'}. Placeholders: {values}"
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
        problems += [f"{c.name}: {x}" for x in _text_problems(p.text, set(placeholders(c)), names)]
    return problems


def _text_problems(text: str, allowed: set[str], names: list[str]) -> list[str]:
    problems = [
        f"unknown placeholder {{{k}}}" for k in _PLACEHOLDER.findall(text) if k not in allowed
    ]
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
        values = placeholders(c)
        if not _text_problems(p.text, set(values), names):
            paragraphs[c.entity_id] = _fill(p.text, values)
    return summary, paragraphs


def _fill(text: str, values: dict[str, str]) -> str:
    return _PLACEHOLDER.sub(lambda m: values[m.group(1)], text).strip()

"""Assemble a Report from candidates, the profile and Gemini's prose."""

import uuid
from datetime import UTC, datetime
from typing import Literal

from app.llm import LLM
from app.models import Candidate, Profile, Report, ReportSection
from app.reports import write
from app.reports.facts import facts_line
from app.reports.rank import co_invest, rank

Kind = Literal["prep", "digest", "memo"]
LIMIT = {"short": 5, "medium": 8, "long": 20}


async def build(
    kind: Kind,
    *,
    llm: LLM,
    profile: Profile,
    candidates: list[Candidate],
    previous: Report | None = None,
    now: datetime | None = None,
    report_id: str | None = None,
) -> Report:
    ranked = rank(candidates, profile)
    context = ""
    if kind == "digest":
        ranked, context = _what_changed(ranked, previous)
    length = "long" if kind == "memo" else profile.style.length
    selected = ranked[: LIMIT[length]]

    report = Report(
        id=report_id or new_report_id(),
        kind=kind,
        created_at=now or datetime.now(UTC),
        profile_version=profile.version,
        summary="",
        sections=[],
        candidates=selected,
    )
    if not selected:
        report.summary = (
            "Nothing new since the last report."
            if kind == "digest"
            else "No startup matches the current profile."
        )
        return report

    summary, paragraphs = await write.write(llm, profile, kind, selected, context)
    report.summary = summary or f"{len(selected)} startups match your thesis."
    report.sections = _sections(kind, selected, paragraphs, profile)
    return report


def new_report_id() -> str:
    return f"rep-{uuid.uuid4().hex[:12]}"


def _what_changed(ranked: list[Candidate], previous: Report | None) -> tuple[list[Candidate], str]:
    if previous is None:
        return ranked, "first digest: everything is new"
    seen = {c.entity_id: {r.entity_id for r in c.rounds} for c in previous.candidates}
    changed = [
        c
        for c in ranked
        if c.entity_id not in seen or {r.entity_id for r in c.rounds} - seen[c.entity_id]
    ]
    new = sum(1 for c in changed if c.entity_id not in seen)
    return changed, f"{new} new startups, {len(changed) - new} with a new round"


def _sections(
    kind: Kind, selected: list[Candidate], paragraphs: dict[str, str], profile: Profile
) -> list[ReportSection]:
    refs = {r.entity_id: r.name for r in profile.reference_investors}
    groups: dict[str, list[Candidate]] = {}
    for c in selected:
        led, joined = co_invest(c, set(refs))
        likely = next((s.value for s in c.signals if s.kind == "likely_to_raise"), None)
        if kind == "digest":
            title = "What changed"
        elif joined:
            title = "Co-invest with investors you trust"
        elif likely is True:
            title = "Likely to raise soon"
        else:
            title = "Other matches"
        groups.setdefault(title, []).append(c)

    short = kind != "memo" and profile.style.length == "short"
    return [
        ReportSection(
            title=title,
            body_md="\n\n".join(_entry(c, paragraphs.get(c.entity_id), refs, short) for c in cs),
            candidate_ids=[c.entity_id for c in cs],
        )
        for title, cs in groups.items()
    ]


def _entry(c: Candidate, paragraph: str | None, refs: dict[str, str], short: bool) -> str:
    lines = [f"**{c.name}**: {paragraph or c.description or ''}".rstrip(": ")]
    with_refs = [
        f"{i.name} ({'lead, ' if i.is_lead else ''}{r.name})"
        for r in c.rounds
        for i in r.investors
        if i.entity_id in refs
    ]
    if with_refs:
        lines.append("Co-invest: " + "; ".join(with_refs))
    if facts := facts_line(c, short=short):
        lines.append(facts)
    return "\n\n".join(lines)

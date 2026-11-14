"""Assemble a Report from candidates, the profile and Gemini's prose."""

import re
import uuid
from datetime import UTC, datetime
from typing import Literal

from app.llm import LLM
from app.models import Candidate, Fact, Profile, Report, ReportSection
from app.reports import write
from app.reports.facts import BADGES, render_date
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
    ranked = rank(candidates, profile, today=now.date() if now else None)
    context = ""
    if kind == "digest":
        ranked, context = _what_changed(ranked, previous)
    length = "long" if kind == "memo" else profile.style.length
    selected = ranked[: min(LIMIT[length], profile.style.max_candidates or LIMIT[length])]

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


def shown_since_prep(reports: list[Report]) -> Report | None:
    """Everything the investor has seen: one report with the union of the candidates (and
    their rounds) of `reports`, newest first, as returned by `store.reports.since_last_prep`.
    A digest only holds what changed, so diffing against the latest one alone would bring
    back startups already shown in the prep report as new."""
    if not reports:
        return None
    merged: dict[str, Candidate] = {}
    for report in reports:
        for c in report.candidates:
            if c.entity_id not in merged:
                merged[c.entity_id] = c
                continue
            known = {r.entity_id for r in merged[c.entity_id].rounds}
            extra = [r for r in c.rounds if r.entity_id not in known]
            if extra:
                merged[c.entity_id] = merged[c.entity_id].model_copy(
                    update={"rounds": merged[c.entity_id].rounds + extra}
                )
    return reports[0].model_copy(update={"candidates": list(merged.values())})


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
    refs = {r.entity_id for r in profile.reference_investors}
    groups: dict[str, list[Candidate]] = {}
    for c in selected:
        led, joined = co_invest(c, refs)
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

    return [
        ReportSection(
            title=title,
            body_md="\n\n".join(
                f"**{c.name}**: {paragraphs[c.entity_id]}"
                for c in cs
                if paragraphs.get(c.entity_id)
            ),
            candidate_ids=[c.entity_id for c in cs],
        )
        for title, cs in groups.items()
    ]


WEB_SECTION = "Web signals (unverified)"


def with_web_signals(report: Report, signals: dict[str, list[Fact]]) -> Report:
    """Append web news in its own section; it never enters the Cala facts or the model's prose."""
    names = {c.entity_id: c.name for c in report.candidates}
    ids = [i for i in names if signals.get(i)]
    if not ids:
        return report
    blocks = []
    for entity_id in ids:
        items = "\n".join(f"- {_web_item(f)}" for f in signals[entity_id])
        blocks.append(f"**{names[entity_id]}**\n\n{items}")
    section = ReportSection(title=WEB_SECTION, body_md="\n\n".join(blocks), candidate_ids=ids)
    return report.model_copy(update={"sections": [*report.sections, section]})


def _web_item(fact: Fact) -> str:
    # Headlines are third-party text: keep them from breaking the Markdown link.
    title = " ".join(re.sub(r"[\[\]()]", " ", str(fact.value)).split())
    source = fact.sources[0] if fact.sources else None
    link = f"[{title}]({source.url})" if source and source.url else title
    where = ", ".join(x for x in (source and source.name, source and render_date(source)) if x)
    return f"{link} ({where + ', ' if where else ''}{BADGES['web_unverified']})"

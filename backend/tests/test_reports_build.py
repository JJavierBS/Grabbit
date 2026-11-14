import re

from app.agent.sources import fixture_candidates
from app.llm.fake import FakeLLM, Script
from app.models import ReferenceInvestor
from app.reports.build import build
from app.reports.facts import placeholders
from app.store.profile import default_profile


def _profile(now, **update):
    return default_profile(now).model_copy(update=update)


async def _build(kind, profile, llm=None, previous=None, candidates=None, now=None):
    return await build(
        kind,
        llm=llm or FakeLLM(),
        profile=profile,
        candidates=fixture_candidates() if candidates is None else candidates,
        previous=previous,
        now=now,
    )


def _body(report):
    return "\n".join(s.body_md for s in report.sections)


async def test_prep_report_explains_fit_and_leaves_facts_to_the_cards(now):
    report = await _build("prep", _profile(now), now=now)
    assert report.summary == "6 Slush attendees match your thesis."
    assert report.profile_version == 1
    body = _body(report)
    assert "**Kiln Analytics**: Energy analytics for industrial kilns" in body
    assert len(report.candidates) == 6


async def test_a_section_states_no_fact_its_cards_already_show(now):
    """#118: prose, a "Last round" line and the fact grid used to repeat the same round."""
    profile = _profile(
        now, reference_investors=[ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")]
    )
    report = await _build("prep", profile, now=now)
    for section in report.sections:
        assert "Last round:" not in section.body_md
        assert "Co-invest:" not in section.body_md
        assert "Stage:" not in section.body_md
        assert not re.search(r"\d", section.body_md)
        for cid in section.candidate_ids:
            c = next(c for c in report.candidates if c.entity_id == cid)
            for value in placeholders(c, badge=False).values():
                if value not in {"not published", "none published"}:
                    assert value not in section.body_md, value


async def test_a_paragraph_that_cites_values_is_rejected(now):
    cites = Script(
        task="report_write",
        output={
            "summary": "{count} startups.",
            "paragraphs": [{"candidate_id": "cand-kiln", "text": "It raised {last_round_amount}."}],
        },
    )
    llm = FakeLLM(scripts=[cites])
    report = await _build("prep", _profile(now), llm=llm, now=now)
    assert [task for task, _ in llm.calls] == ["report_write", "report_write"]
    assert "do not cite" in llm.calls[1][1]
    assert "It raised" not in _body(report)


async def test_the_writer_is_told_what_the_cards_show_and_whom_you_trust(now):
    llm = FakeLLM()
    profile = _profile(
        now, reference_investors=[ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")]
    )
    await _build("prep", profile, llm=llm, now=now)
    [(_, prompt)] = llm.calls
    assert "Investors you trust among them: Fjord Capital" in prompt
    assert "{last_round_amount}" not in prompt
    from app.reports.write import SYSTEM

    assert "Do not repeat any of them" in SYSTEM
    assert "[Database]" in SYSTEM


async def test_new_instructions_change_the_report(now):
    before = await _build("prep", _profile(now), now=now)
    after = await _build(
        "prep",
        _profile(now, instructions="Lead with co-investors. Two lines per startup."),
        now=now,
    )
    assert before.summary != after.summary
    assert after.summary == "Co-investments first: 6 startups, kept short."


async def test_filters_change_the_report(now):
    profile = _profile(now)
    profile.filters.sectors_out = ["B2C"]
    report = await _build("prep", profile, now=now)
    assert {c.name for c in report.candidates} == {
        "Kiln Analytics",
        "Ledgerly",
        "Tundra Grid",
        "Brikk",
    }


async def test_short_style_limits_startups_and_sentences(now):
    profile = _profile(now)
    profile.style.length = "short"
    llm = FakeLLM()
    report = await _build("prep", profile, llm=llm, now=now)
    assert len(report.candidates) == 5
    assert "one sentence per startup" in llm.calls[0][1]


async def test_reference_investors_get_their_own_section(now):
    profile = _profile(
        now, reference_investors=[ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")]
    )
    report = await _build("prep", profile, now=now)
    first = report.sections[0]
    assert first.title == "Co-invest with investors you trust"
    assert first.candidate_ids == ["cand-ledgerly", "cand-brikk"]
    # Who you trust shows in the card's co-invest signal, not again in the prose.
    assert "Co-invest:" not in first.body_md


async def test_numbers_written_by_the_model_are_rejected_then_replaced(now):
    bad = Script(
        task="report_write",
        output={
            "summary": "Six startups, total EUR 40M.",
            "paragraphs": [{"candidate_id": "cand-kiln", "text": "Raised 2 million in 2024."}],
        },
    )
    llm = FakeLLM(scripts=[bad])
    report = await _build("prep", _profile(now), llm=llm, now=now)
    assert [task for task, _ in llm.calls] == ["report_write", "report_write"]
    assert "rules" in llm.calls[1][1]
    assert report.summary == "6 startups match your thesis."
    body = _body(report)
    assert "2 million" not in body and "40M" not in body
    # No valid paragraph: the card under the section carries Kiln's description and facts.
    kiln = next(s for s in report.sections if "cand-kiln" in s.candidate_ids)
    assert "**Kiln Analytics**" not in kiln.body_md


async def test_unknown_placeholder_is_rejected(now):
    bad = Script(
        task="report_write",
        output={
            "summary": "{count} startups.",
            "paragraphs": [{"candidate_id": "cand-kiln", "text": "Valued at {valuation}."}],
        },
    )
    report = await _build("prep", _profile(now), llm=FakeLLM(scripts=[bad]), now=now)
    assert "{valuation}" not in _body(report) and "Valued at" not in _body(report)


async def test_model_down_still_produces_a_report_from_facts(now):
    report = await _build("prep", _profile(now), llm=FakeLLM(scripts=[]), now=now)
    assert report.summary == "6 startups match your thesis."
    assert len(report.candidates) == 6
    assert sorted(i for s in report.sections for i in s.candidate_ids) == sorted(
        c.entity_id for c in report.candidates
    )


async def test_digest_with_nothing_new(now):
    first = await _build("prep", _profile(now), now=now)
    digest = await _build("digest", _profile(now), previous=first, now=now)
    assert digest.summary == "Nothing new since the last report."
    assert digest.sections == [] and digest.candidates == []


async def test_digest_keeps_only_new_rounds_and_new_startups(now):
    candidates = fixture_candidates()
    first = await _build(
        "prep", _profile(now), candidates=[c.model_copy(deep=True) for c in candidates[:5]], now=now
    )
    candidates[0].rounds[0] = candidates[0].rounds[0].model_copy(update={"entity_id": "r-new"})
    digest = await _build("digest", _profile(now), previous=first, candidates=candidates, now=now)
    assert {c.entity_id for c in digest.candidates} == {"cand-kiln", "cand-sauna"}
    assert [s.title for s in digest.sections] == ["What changed"]


async def test_memo_is_long_whatever_the_style(now):
    profile = _profile(now)
    profile.style.length = "short"
    llm = FakeLLM()
    memo = await _build("memo", profile, llm=llm, now=now)
    assert len(memo.candidates) == 6
    assert "a short paragraph per startup" in llm.calls[0][1]


async def test_no_digit_in_prose_comes_from_the_model(now):
    report = await _build("prep", _profile(now), now=now)
    for section in report.sections:
        for line in section.body_md.split("\n\n"):
            if line.startswith(("Last round:", "Co-invest:")):
                continue
            prose = re.sub(r"\([^)]*\)", "", line)
            for token in re.findall(r"[^ ]*\d[^ ]*", prose):
                assert token.rstrip(".,;") in _rendered_values(report), token


def _rendered_values(report):
    from app.reports.facts import placeholders

    values = set()
    for c in report.candidates:
        for v in placeholders(c).values():
            values |= {t.rstrip(".,;") for t in v.split()}
    return values


async def test_prose_has_no_badges_and_no_doubled_round(now):
    echo = Script(
        task="report_write",
        output={
            "summary": "{count} startups.",
            "paragraphs": [
                {
                    "candidate_id": "cand-kiln",
                    "text": "Climate software (Official filing) backed by North Pine Ventures "
                    "[Press], ahead of its next Equity round round.",
                }
            ],
        },
    )
    report = await _build("prep", _profile(now), llm=FakeLLM(scripts=[echo]), now=now)
    kiln = next(s for s in report.sections if "cand-kiln" in s.candidate_ids).body_md
    [prose] = [p for p in kiln.split("\n\n") if p.startswith("**Kiln")]
    assert prose == (
        "**Kiln Analytics**: Climate software backed by North Pine Ventures, "
        "ahead of its next Equity round."
    )


def test_shown_since_prep_merges_candidates_and_rounds():
    from app.reports.build import shown_since_prep

    def report(rid, kind, candidates):
        from datetime import UTC, datetime

        from app.models import Report

        return Report(
            id=rid,
            kind=kind,
            created_at=datetime(2026, 11, 14, tzinfo=UTC),
            profile_version=1,
            summary="",
            sections=[],
            candidates=candidates,
        )

    a, b, *_ = fixture_candidates()
    a_new_round = a.model_copy(
        update={"rounds": [a.rounds[0].model_copy(update={"entity_id": "r-new"})]}
    )
    merged = shown_since_prep([report("d", "digest", [a_new_round]), report("p", "prep", [a, b])])
    assert [c.entity_id for c in merged.candidates] == [a.entity_id, b.entity_id]
    rounds = {r.entity_id for r in merged.candidates[0].rounds}
    assert "r-new" in rounds and a.rounds[0].entity_id in rounds
    assert shown_since_prep([]) is None

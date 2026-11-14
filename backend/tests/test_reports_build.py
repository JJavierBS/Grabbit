import re

from app.agent.sources import fixture_candidates
from app.llm.fake import FakeLLM, Script
from app.models import ReferenceInvestor
from app.reports.build import build
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


async def test_prep_report_renders_values_from_facts(now):
    report = await _build("prep", _profile(now), now=now)
    assert report.summary == "6 Slush attendees match your thesis."
    assert report.profile_version == 1
    body = _body(report)
    assert "Its Seed of EUR 2M closed in May 2024, led by North Pine Ventures." in body
    assert "Last round: Seed, EUR 2M (Press), May 2024 (Official filing)" in body
    assert "Team size is not published" in body
    assert len(report.candidates) == 6


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


async def test_short_style_limits_and_trims_facts(now):
    profile = _profile(now)
    profile.style.length = "short"
    report = await _build("prep", profile, now=now)
    assert len(report.candidates) == 5
    assert "Stage:" not in _body(report) and "Last round:" in _body(report)


async def test_reference_investors_get_their_own_section(now):
    profile = _profile(
        now, reference_investors=[ReferenceInvestor(entity_id="inv-fjord", name="Fjord Capital")]
    )
    report = await _build("prep", profile, now=now)
    first = report.sections[0]
    assert first.title == "Co-invest with investors you trust"
    assert first.candidate_ids == ["cand-ledgerly", "cand-brikk"]
    assert "Co-invest: Fjord Capital (lead, Series A)" in first.body_md


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
    kiln = next(s for s in report.sections if "cand-kiln" in s.candidate_ids)
    assert "**Kiln Analytics**: Energy analytics" in kiln.body_md


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
    assert "Last round:" in _body(report)


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
    memo = await _build("memo", profile, now=now)
    assert len(memo.candidates) == 6 and "Stage:" in _body(memo)


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
                    "text": "Based in {hq} (Official filing) and led by {last_round_lead}, "
                    "with {last_round_co_investors} joining; raised {last_round_amount} [Press] "
                    "in its {last_round} round.",
                }
            ],
        },
    )
    report = await _build("prep", _profile(now), llm=FakeLLM(scripts=[echo]), now=now)
    kiln = next(s for s in report.sections if "cand-kiln" in s.candidate_ids).body_md
    [prose] = [p for p in kiln.split("\n\n") if p.startswith("**Kiln")]
    assert "Based in Finland and led by North Pine Ventures, with Aurora Angels" in prose
    assert "raised EUR 2M in its Seed round." in prose
    assert "(Press)" in kiln  # the facts line under the prose keeps the badges

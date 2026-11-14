from datetime import UTC, datetime

from app.agent import sources
from app.agent.sources import candidates_for, fixture_candidates
from app.discovery.pipeline import DiscoveryResult, DiscoveryStats
from app.models import ReferenceInvestor
from app.references import remember, resolve_references
from app.reports import service
from app.signals.core import co_invest
from app.store import profile as profile_store
from app.store.db import init_db

NOW = datetime(2026, 11, 14, 12, 0, tzinfo=UTC)


def _profile_with(*refs: ReferenceInvestor):
    return profile_store.default_profile(NOW).model_copy(update={"reference_investors": list(refs)})


def test_unresolved_name_gets_the_cala_entity_id():
    profile = _profile_with(
        ReferenceInvestor(entity_id="unresolved:aurora angels", name="Aurora Angels"),
        ReferenceInvestor(entity_id="unresolved:nobody", name="Nobody Capital"),
    )

    resolved = resolve_references(profile, fixture_candidates())

    assert [r.entity_id for r in resolved.reference_investors] == [
        "inv-aurora",
        "unresolved:nobody",
    ]


def test_name_match_ignores_case_punctuation_and_legal_suffix():
    profile = _profile_with(
        ReferenceInvestor(entity_id="unresolved:fjord", name="fjord capital, ltd.")
    )

    resolved = resolve_references(profile, fixture_candidates())

    assert resolved.reference_investors[0].entity_id == "inv-fjord"


def test_an_investor_seen_only_in_filtered_out_startups_still_resolves():
    remember({"lifeline ventures": "inv-lifeline"})
    profile = _profile_with(
        ReferenceInvestor(entity_id="unresolved:lifeline ventures", name="Lifeline Ventures")
    )

    resolved = resolve_references(profile, [])

    assert resolved.reference_investors[0].entity_id == "inv-lifeline"


def test_resolved_ids_are_left_alone():
    profile = _profile_with(ReferenceInvestor(entity_id="inv-birch", name="Aurora Angels"))

    assert resolve_references(profile, fixture_candidates()) is profile


async def test_co_invest_signal_fires_for_a_name_typed_in_chat(monkeypatch):
    profile = _profile_with(
        ReferenceInvestor(entity_id="unresolved:aurora angels", name="Aurora Angels")
    )

    async def pipeline(client, profile, today=None, limits=None):
        # What discovery computes before the name is linked: no match by id.
        found = [
            c.model_copy(update={"signals": [co_invest(c, profile.reference_investors)]})
            for c in fixture_candidates()
        ]
        return DiscoveryResult(candidates=found, stats=DiscoveryStats())

    monkeypatch.setattr(sources, "get_candidates", pipeline)

    candidates = await candidates_for(profile)

    mossa = next(c for c in candidates if c.entity_id == "cand-mossa")
    signal = next(s for s in mossa.signals if s.kind == "co_invest")
    assert signal.value == ["Aurora Angels"]


async def test_report_groups_co_investments_for_a_name_typed_in_chat():
    init_db()
    profile = _profile_with(
        ReferenceInvestor(entity_id="unresolved:aurora angels", name="Aurora Angels")
    )

    report = await service.run("prep", profile=profile, now=NOW)

    titles = [section.title for section in report.sections]
    assert titles[0] == "Co-invest with investors you trust"
    assert "cand-mossa" in report.sections[0].candidate_ids

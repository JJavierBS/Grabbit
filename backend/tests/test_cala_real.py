"""Real Cala responses (recorded 2026-11-14 from Slush 2026 attendees) through our parsing."""

from typing import get_args

from app.discovery.build import build_candidate, build_round, issuer_round_ids
from app.discovery.filters import is_startup
from app.models import TrustLevel
from tests.conftest import load_cala

RUPERT_SEED = "9f1df8bf-e814-5361-aa79-0840a4671eb1"


def test_real_round_falls_back_to_announcement_date_and_reads_leads():
    round_ = build_round(load_cala("real_round_rupert_seed"))
    assert round_.name == "Seed"
    assert round_.date.value is not None  # no event_date in this round: announcement_date
    leads = sorted(i.name for i in round_.investors if i.is_lead)
    assert leads == ["Cortical Ventures", "IA Ventures"]
    # Participants without is_lead are plain investors, and the issuer is not one of them.
    assert "Rupert" not in [i.name for i in round_.investors]
    assert len(round_.investors) == 11


def test_real_startup_builds_a_valid_candidate():
    company = load_cala("real_company_rupert")
    assert issuer_round_ids(company) == [RUPERT_SEED]
    candidate = build_candidate(company, [build_round(load_cala("real_round_rupert_seed"))])
    assert candidate.funding_stage.value == "SEED"
    assert candidate.founding_date.trust == "not_published"  # absent in Cala, never invented
    levels = set(get_args(TrustLevel))
    facts = [candidate.funding_stage, candidate.hq, candidate.headcount, candidate.total_funding]
    facts += [f for r in candidate.rounds for f in (r.amount, r.date)]
    assert all(f.trust in levels for f in facts)
    assert all(s.url is None or s.url.startswith("http") for f in facts for s in f.sources)


def test_real_startup_passes_the_startup_rules():
    from datetime import date

    assert is_startup(load_cala("real_company_rupert"), date(2026, 11, 14))

from app.agent.onboarding import money, pick_questions
from app.agent.sources import fixture_candidates
from app.models import ReferenceInvestor
from app.store.profile import default_profile


def _candidates():
    return fixture_candidates()


def test_picks_two_or_three_questions_with_numbers_from_the_data(now):
    questions = pick_questions(_candidates(), default_profile(now), now)
    assert 2 <= len(questions) <= 3
    texts = {q.key: q.text for q in questions}
    assert texts["stage"].startswith("Of the 6 startups that match, 4 are pre-seed or seed and 2")


def test_ticket_question_uses_round_amounts(now):
    questions = pick_questions(_candidates(), default_profile(now), now, limit=10)
    ticket = next(q for q in questions if q.key == "ticket")
    assert "EUR 400k to EUR 22M" in ticket.text


def test_investor_question_counts_backed_attendees(now):
    profile = default_profile(now).model_copy(
        update={
            "reference_investors": [
                ReferenceInvestor(entity_id="inv-north-pine", name="North Pine")
            ]
        }
    )
    questions = pick_questions(_candidates(), profile, now, limit=10)
    text = next(q.text for q in questions if q.key == "investors")
    assert text.startswith("4 attendees are backed by North Pine")


def test_answered_filters_are_not_asked_again(now):
    profile = default_profile(now)
    profile.filters.sectors_out = ["B2C"]
    profile.filters.countries = ["Finland"]
    keys = {q.key for q in pick_questions(_candidates(), profile, now, limit=10)}
    assert "industries" not in keys and "hq" not in keys


def test_no_candidates_means_no_questions(now):
    assert pick_questions([], default_profile(now), now) == []


def test_money_formatting():
    assert money(400000, "EUR") == "EUR 400k"
    assert money(22_000_000, "EUR") == "EUR 22M"
    assert money(1_500_000, "USD") == "USD 1.5M"

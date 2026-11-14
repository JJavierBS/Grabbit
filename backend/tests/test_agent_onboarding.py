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


def test_every_question_offers_short_clickable_answers(now):
    questions = pick_questions(_candidates(), default_profile(now), now, limit=10)
    assert questions
    for q in questions:
        assert 1 <= len(q.options) <= 4, q.key
        for label, answer in q.options:
            assert 0 < len(label) <= 32 and answer.endswith("."), (q.key, label, answer)


def test_answers_are_built_from_the_same_data_as_the_question(now):
    by_key = {q.key: q for q in pick_questions(_candidates(), default_profile(now), now, limit=10)}
    ticket = by_key["ticket"]
    low = ticket.text.split("range from ")[1].split(" to ")[0]
    assert ticket.options[0] == (f"Small, near {low}", f"I invest in small rounds, near {low}.")
    investors = by_key["investors"]
    top = investors.text.split("? ")[1].split(" back the most")[0].split(" and ")
    assert [label for label, _ in investors.options][: len(top)] == top


def _bank(now):
    return pick_questions(_candidates(), default_profile(now), now, limit=None)


def _llm(*questions):
    from app.llm.fake import FakeLLM, Script

    return FakeLLM([Script(task="questions", output={"questions": list(questions)})])


def _worded(q, text, labels=None):
    labels = labels or [label for label, _ in q.options]
    return {
        "key": q.key,
        "text": text,
        "options": [{"label": lb, "answer": f"{lb}, por favor."} for lb in labels],
    }


async def test_the_model_picks_and_words_the_questions_in_the_investors_language(now):
    """#165: the same three English templates every time, whatever the investor said."""
    from app.agent.onboarding import word_questions

    bank = _bank(now)
    ticket = next(q for q in bank if q.key == "ticket")
    stage = next(q for q in bank if q.key == "stage")
    llm = _llm(
        _worded(
            ticket,
            "Las rondas van de 400k a 22M EUR. ¿Qué ticket sueles poner?",
            ["Pequeño, unos 400k", "Grande, unos 22M", "Me da igual"],
        ),
        _worded(
            stage,
            "De 6 startups, 4 son pre-semilla o semilla y 2 Serie A. ¿Qué etapa?",
            ["Pre-semilla y semilla", "Serie A o más", "Cualquiera"],
        ),
    )

    asked = await word_questions(llm, "Invierto en IA, tickets pequeños", bank)

    assert [q.key for q in asked] == ["ticket", "stage"]
    assert asked[0].text.startswith("Las rondas van de 400k a 22M EUR")
    assert asked[0].options[0] == ("Pequeño, unos 400k", "Pequeño, unos 400k, por favor.")
    task, prompt = llm.calls[-1]
    assert task == "questions" and "Invierto en IA, tickets pequeños" in prompt


async def test_a_worded_question_that_changes_a_number_keeps_the_banks_wording(now):
    from app.agent.onboarding import word_questions

    bank = _bank(now)
    stage = next(q for q in bank if q.key == "stage")
    llm = _llm(_worded(stage, "De 7 startups, 4 son semilla y 2 Serie A. ¿Qué etapa?"))

    asked = await word_questions(llm, "hola", bank)

    assert asked == [stage]


async def test_a_worded_question_that_drops_an_option_keeps_the_banks_wording(now):
    from app.agent.onboarding import word_questions

    bank = _bank(now)
    stage = next(q for q in bank if q.key == "stage")
    llm = _llm(_worded(stage, stage.text, ["Seed"]))

    assert await word_questions(llm, "hola", bank) == [stage]


async def test_unknown_keys_or_a_model_failure_fall_back_to_the_top_of_the_bank(now):
    from app.agent.onboarding import word_questions
    from app.llm.fake import FakeLLM

    bank = _bank(now)
    made_up = {"key": "vibes", "text": "¿Buen rollo?", "options": []}
    assert await word_questions(_llm(made_up), "hola", bank) == bank[:3]
    assert await word_questions(FakeLLM([]), "hola", bank) == bank[:3]
    assert await word_questions(FakeLLM([]), "hola", []) == []

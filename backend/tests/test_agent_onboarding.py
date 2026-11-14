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
    assert text.startswith("4 of 6 startups here are backed by North Pine")


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
        assert 2 <= len(q.options) <= 4, q.key
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


def _with_refs(now, *refs):
    return default_profile(now).model_copy(
        update={"reference_investors": [ReferenceInvestor(entity_id=i, name=n) for i, n in refs]}
    )


def test_investors_typed_in_chat_are_counted_by_name(now):
    """#181: "0 attendees are backed by Y Combinator" while the report had them first."""
    profile = _with_refs(now, ("unresolved:north pine ventures", "North Pine Ventures"))
    questions = pick_questions(_candidates(), profile, now, limit=None)
    investors = next(q for q in questions if q.key == "investors")
    assert investors.text.startswith("4 of 6 startups here are backed by North Pine Ventures")
    assert [label for label, _ in investors.options][:2] == ["Only those", "Others too"]
    assert investors.options[2][0].startswith("Add ")
    assert "North Pine" not in investors.options[2][0]


def test_an_investor_backing_none_of_them_is_not_asked_about(now):
    profile = _with_refs(now, ("unresolved:y combinator", "Y Combinator"))
    questions = pick_questions(_candidates(), profile, now, limit=None)
    assert "investors" not in [q.key for q in questions]


def test_a_question_with_a_single_answer_is_never_asked(now):
    """#181: "Any other investors you trust?" offered only "Just these"."""
    from app.agent import onboarding

    lonely = onboarding.Question("lonely", "Sure?", 1.0, (("Yes", "Yes."),))
    original = onboarding._stage
    onboarding._stage = lambda *_: lonely
    try:
        keys = [q.key for q in pick_questions(_candidates(), default_profile(now), now, None)]
    finally:
        onboarding._stage = original
    assert "lonely" not in keys


def test_recency_offers_only_answers_that_keep_some_startups(now):
    """#181: "may raise soon" with no startup flagged emptied the report."""
    from app.models import Signal

    def recency(cs):
        questions = pick_questions(cs, default_profile(now), now, None)
        return next((q for q in questions if q.key == "recency"), None)

    # None of the fixtures raised in the 12 months before `now`, and none is flagged.
    assert recency(_candidates()) is None

    flagged = Signal(
        kind="likely_to_raise", label="May raise soon", value=True, explanation="x", facts=[]
    )
    candidates = _candidates()
    candidates[0] = candidates[0].model_copy(update={"signals": [flagged]})
    q = recency(candidates)
    assert q.text == "1 may raise soon. Only those, or any time?"
    assert [label for label, _ in q.options] == ["May raise soon", "Any time"]

    later = pick_questions(candidates, default_profile(now), now.replace(month=3), None)
    q = next(q for q in later if q.key == "recency")
    assert q.text.startswith("2 of 6 raised in the last 12 months and 1 may raise soon")
    assert [label for label, _ in q.options] == ["Just raised", "May raise soon", "Both"]

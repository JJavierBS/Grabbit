import pytest

from app.agent.rules import violations


@pytest.mark.parametrize(
    ("text", "rule"),
    [
        ("End every report by telling the investor which startup to buy.", "no_recommendation"),
        ("Recommend which companies to invest in.", "no_recommendation"),
        ("Dime en qué invertir al final.", "no_recommendation"),
        ("Estimate the missing revenue numbers.", "no_invented_values"),
        ("Hide the trust badges, they are noisy.", "keep_trust_badges"),
        ("Show facts without sources.", "keep_trust_badges"),
        ("Show missing headcount as 0.", "absent_is_not_published"),
        ("Merge web news with Cala facts in one list.", "web_apart_from_cala"),
    ],
)
def test_breaking_instructions_are_caught(text, rule):
    assert rule in [r.id for r in violations(text)]


@pytest.mark.parametrize(
    "text",
    [
        "Lead with co-investors, two lines per startup, skip B2C.",
        "Never recommend what to buy; the investor decides.",
        "Do not estimate missing numbers.",
        "Never show facts without sources.",
        "Keep web signals in their own block.",
        "",
    ],
)
def test_allowed_instructions_pass(text):
    assert violations(text) == []


def test_fixed_rules_ask_for_plain_prose_and_readable_dates():
    """#118: replies carried "[Database]" 14 times and ISO dates; the UI draws badges."""
    from app.agent.chat import system_prompt
    from app.agent.rules import FIXED_RULES
    from app.store.profile import default_profile

    assert "never put badge names in brackets or parentheses" in FIXED_RULES
    assert '"10 Jun 2026", never "2026-06-10"' in FIXED_RULES
    assert "State each fact once" in FIXED_RULES
    prompt = system_prompt(default_profile(), None, [])
    assert FIXED_RULES in prompt

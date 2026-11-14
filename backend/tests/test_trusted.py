import pytest

from app.discovery import links
from app.models import ReferenceInvestor
from app.trusted import Trusted

YC = ReferenceInvestor(entity_id="yc-company", name="Y Combinator")
FIVE_HUNDRED = ReferenceInvestor(entity_id="500", name="500 Global")
UGLY = ReferenceInvestor(entity_id="unresolved:Ugly", name="Ugly")


@pytest.mark.parametrize(
    ("entity_id", "name", "expected"),
    [
        ("yc-company", "Anything", YC),
        ("yc-organization", "Y Combinator", YC),
        ("yc-w24", "Y Combinator W24", YC),
        ("500-europe", "500 Global (500 Emerging Europe)", FIVE_HUNDRED),
        ("500-inc", "500 Global, Inc.", FIVE_HUNDRED),
        ("yc-llc", "Y Combinator Management, LLC", YC),
        ("yc-co", "Y Combinator Co", YC),
        ("udv", "Ugly Duckling Ventures", None),
        ("combinator", "Combinator", None),
        ("nameless", None, None),
        (None, "Y Combinator", YC),
    ],
)
def test_matches_by_entity_id_or_fund_name(entity_id, name, expected):
    assert Trusted([YC, FIVE_HUNDRED, UGLY]).match(entity_id, name) == expected


def test_a_longer_reference_matches_the_plain_fund_name():
    vehicle = ReferenceInvestor(entity_id="500-europe", name="500 Global (500 Emerging Europe)")
    assert Trusted([vehicle]).match("500", "500 Global") == vehicle


def test_hidden_links_and_signals_share_one_matcher():
    assert links.Trusted is Trusted

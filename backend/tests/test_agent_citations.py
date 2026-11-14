"""Sources under a chat reply (#141): from the candidates' facts, never from the model."""

from app.agent.citations import MAX_STARTUPS, reply_sources
from app.agent.sources import fixture_candidates
from app.models import Fact, Source

CANDIDATES = fixture_candidates()


def by_id(entity_id: str):
    return next(c for c in CANDIDATES if c.entity_id == entity_id)


def test_each_named_startup_gets_its_sources_in_the_order_the_reply_names_them():
    text = "Ledgerly raised a seed. Kiln Analytics did too, and kiln analytics is hiring."
    cited = reply_sources(text, CANDIDATES)
    assert [c.name for c in cited] == ["Ledgerly", "Kiln Analytics"]
    kiln = cited[1]
    # Strongest first, each source once.
    assert [(s.name, s.rank) for s in kiln.sources] == [
        ("Trade register", "filing"),
        ("Company website", "primary"),
        ("Press release", "press"),
        ("Funding database", "aggregator"),
    ]


def test_a_reply_naming_no_startup_cites_nothing():
    assert reply_sources("Noted. From now on: shorter reports.", CANDIDATES) == []


def test_names_match_whole_words_only():
    brikk = by_id("cand-brikk")
    assert reply_sources("Brikkworks is unrelated.", [brikk]) == []
    assert reply_sources("What about brikk?", [brikk])[0].name == "Brikk"


def test_a_vehicle_name_is_matched_by_its_short_name():
    fund = by_id("cand-mossa").model_copy(update={"name": "Mossa Health (Mossa Health Oy)"})
    assert reply_sources("Mossa Health fits.", [fund])[0].entity_id == "cand-mossa"


def test_unpublished_values_cite_nothing_and_unsourced_values_cite_cala():
    bare = by_id("cand-tundra").model_copy(
        update={
            "founding_date": Fact(value="2021", trust="aggregator", sources=[]),
            "funding_stage": Fact.not_published(),
            "headcount": Fact.not_published(),
            "total_funding": Fact.not_published(),
            "hq": Fact.not_published(),
            "rounds": [],
        }
    )
    assert reply_sources("Tundra Grid", [bare])[0].sources == [
        Source(name="Cala", rank="aggregator")
    ]
    nothing = bare.model_copy(update={"founding_date": Fact.not_published()})
    assert reply_sources("Tundra Grid", [nothing]) == []


def test_one_source_keeps_its_strongest_level():
    kiln = by_id("cand-kiln")
    weak = Fact(value="Helsinki", trust="aggregator", sources=[Source(name="X", rank="aggregator")])
    strong = Fact(value="seed", trust="filing", sources=[Source(name="X", rank="filing")])
    kiln = kiln.model_copy(update={"hq": weak, "funding_stage": strong})
    x = next(s for s in reply_sources("Kiln Analytics", [kiln])[0].sources if s.name == "X")
    assert x.rank == "filing"


def test_at_most_a_few_startups_are_cited():
    base = by_id("cand-kiln")
    many = [base.model_copy(update={"entity_id": f"c{i}", "name": f"Startup{i}"}) for i in range(9)]
    text = " ".join(c.name for c in many)
    assert len(reply_sources(text, [*many])) == MAX_STARTUPS

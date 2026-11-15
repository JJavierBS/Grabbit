"""#226: third-party report text reads in the conversation language, originals kept."""

from app.agent.sources import fixture_candidates
from app.llm import LLMError
from app.llm.fake import FakeLLM, Script
from app.models import Fact, NewsItem, Original, Report
from app.reports import service
from app.reports.build import WEB_SECTION
from app.reports.translate import report_texts, translate_texts, with_translations
from app.store import translations as store
from app.store.profile import default_profile
from app.store.translations import Translation
from tests.test_context_dev_signals import FakeWeb, _article

GERMAN = "Grei hat 2,5 Millionen Euro von Cherry Ventures eingesammelt."
SPANISH = "Grei ha recaudado 2,5 millones de euros de Cherry Ventures."
ENGLISH = "Grei opens a Berlin office."


def _llm(items: list[dict]) -> FakeLLM:
    return FakeLLM(scripts=[Script(task="translate", output={"items": items})])


def _german(id_: str, text: str = SPANISH) -> dict:
    return {"id": id_, "language": "de", "language_name": "German", "text": text}


class FailingLLM(FakeLLM):
    async def generate(self, **kwargs):
        self.calls.append((kwargs["task"], kwargs["prompt"]))
        raise LLMError("translate: Gemini unreachable")


async def test_only_text_in_another_language_is_translated():
    llm = _llm([_german("0"), {"id": "1", "language": "es", "text": ""}])

    out = await translate_texts(llm, [GERMAN, "Ya en español."], "es")

    assert out == {GERMAN: Translation(language="de", language_name="German", text=SPANISH)}
    assert llm.calls[0][0] == "translate"


async def test_a_translation_is_cached_per_target_language():
    llm = _llm([_german("0")])
    await translate_texts(llm, [GERMAN], "es")

    again = await translate_texts(llm, [GERMAN], "es-ES")

    assert again[GERMAN].text == SPANISH
    assert len(llm.calls) == 1
    await translate_texts(llm, [GERMAN], "en")
    assert len(llm.calls) == 2


async def test_text_in_the_target_language_is_not_asked_again():
    llm = _llm([{"id": "0", "language": "en", "text": ""}])

    assert await translate_texts(llm, [ENGLISH], "en") == {}
    assert await translate_texts(llm, [ENGLISH], "en") == {}
    assert len(llm.calls) == 1


async def test_a_translation_that_changes_a_number_keeps_the_original():
    llm = _llm([_german("0", "Grei ha recaudado 3,5 millones de euros de Cherry Ventures.")])

    assert await translate_texts(llm, [GERMAN], "es") == {}


async def test_a_gemini_failure_keeps_originals_and_asks_again_next_time():
    llm = FailingLLM(scripts=[])

    assert await translate_texts(llm, [GERMAN], "es") == {}
    assert await translate_texts(llm, [GERMAN], "es") == {}
    assert len(llm.calls) == 2


async def test_an_answer_for_an_unknown_id_is_ignored():
    llm = _llm([_german("7"), _german("x")])

    assert await translate_texts(llm, [GERMAN], "es") == {}


def test_translated_description_and_news_keep_their_original(now):
    c = fixture_candidates()[0].model_copy(
        update={
            "description": GERMAN,
            "news": [NewsItem(title=GERMAN, summary=ENGLISH, date=Fact.not_published())],
        }
    )
    report = Report(
        id="r",
        kind="prep",
        created_at=now,
        profile_version=1,
        summary="",
        sections=[],
        candidates=[c],
    )
    done = {GERMAN: Translation(language="de", language_name="German", text=SPANISH)}

    out = with_translations(report, done).candidates[0]

    assert out.description == SPANISH
    assert out.description_original == Original(language="de", text=GERMAN)
    assert out.news[0].title == SPANISH
    assert out.news[0].title_original == Original(language="de", text=GERMAN)
    assert out.news[0].summary == ENGLISH and out.news[0].summary_original is None
    assert report_texts(report, {"x": [Fact(value=ENGLISH, trust="web_unverified")]}) == [
        GERMAN,
        GERMAN,
        ENGLISH,
        ENGLISH,
    ]


async def test_the_report_reads_in_the_profile_language(now):
    profile = default_profile(now)
    profile = profile.model_copy(
        update={"style": profile.style.model_copy(update={"language": "es"})}
    )
    first = fixture_candidates()[0]
    headline = "Kiln eröffnet ein Büro in Stockholm"
    store.put_many(
        {
            first.description: Translation(
                language="en", language_name="English", text="Descripción traducida."
            ),
            headline: Translation(
                language="de", language_name="German", text="Kiln abre una oficina en Estocolmo"
            ),
        },
        "es",
    )
    web = FakeWeb({"Kiln Analytics": [_article("s1", headline)]})

    report = await service.run("prep", llm=FakeLLM(), web=web, profile=profile, now=now)

    card = next(c for c in report.candidates if c.entity_id == first.entity_id)
    assert card.description == "Descripción traducida."
    assert card.description_original == Original(language="en", text=first.description)
    section = report.sections[-1]
    assert section.title == WEB_SECTION
    assert "[Kiln abre una oficina en Estocolmo](https://news.example/s1)" in section.body_md
    assert "Web, unverified, translated from German)" in section.body_md
    assert headline not in section.body_md

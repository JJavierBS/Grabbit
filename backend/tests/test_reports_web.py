from app.llm.fake import FakeLLM
from app.models import Fact, Source
from app.reports import service
from app.reports.build import WEB_SECTION, with_web_signals
from app.store.profile import default_profile
from tests.test_context_dev_signals import FakeWeb, _article

NEWS = Fact(
    value="Kiln [opens] office",
    trust="web_unverified",
    sources=[
        Source(
            name="Nordic Wire",
            url="https://news.example/s1",
            date="2026-10-02",
            date_precision="day",
            rank="web_unverified",
        )
    ],
)


async def _report(now, web=None, llm=None):
    return await service.run(
        "prep", llm=llm or FakeLLM(), web=web or FakeWeb({}), profile=default_profile(now), now=now
    )


async def test_web_signals_get_their_own_last_section(now):
    report = await _report(now)
    cala_sections = [s.model_copy() for s in report.sections]
    with_web = with_web_signals(report, {"cand-kiln": [NEWS]})

    assert with_web.sections[:-1] == cala_sections
    web = with_web.sections[-1]
    assert web.title == WEB_SECTION and web.candidate_ids == ["cand-kiln"]
    assert web.body_md == (
        "**Kiln Analytics**\n\n- [Kiln opens office](https://news.example/s1) "
        "(Nordic Wire, 2 October 2026, Web, unverified)"
    )


async def test_no_signals_no_section(now):
    report = await _report(now)
    assert WEB_SECTION not in [s.title for s in report.sections]


async def test_service_adds_web_news_without_showing_it_to_the_model(now):
    llm = FakeLLM()
    web = FakeWeb({"Kiln Analytics": [_article("s1", "Kiln opens a Stockholm office")]})
    report = await _report(now, web=web, llm=llm)

    assert report.sections[-1].title == WEB_SECTION
    assert "Kiln opens a Stockholm office" in report.sections[-1].body_md
    cala_text = "\n".join(s.body_md for s in report.sections[:-1])
    assert "Stockholm" not in cala_text
    assert all("Stockholm" not in prompt for _, prompt in llm.calls)

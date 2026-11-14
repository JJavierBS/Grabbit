from datetime import UTC, datetime

from app.agent.sources import fixture_candidates
from app.agent.visual import visual_answer
from app.llm import ChatResult
from app.store import profile as profile_store

PROFILE = profile_store.default_profile(datetime(2026, 11, 14, tzinfo=UTC))


class Stub:
    def __init__(self, text):
        self.text = text
        self.system = ""

    async def chat(self, *, system, messages, tools=None):
        self.system = system
        return ChatResult(text=self.text)


async def test_the_visual_answer_lists_report_ids_and_strips_a_code_fence():
    llm = Stub(
        '```openui\nroot = Answer([t, g])\nt = Text("Aurora led it.")\n'
        'g = CompanyGraph("cand-mossa")\n```'
    )

    ui = await visual_answer(llm, "Why Mossa?", PROFILE, fixture_candidates())

    assert ui == 'root = Answer([t, g])\nt = Text("Aurora led it.")\ng = CompanyGraph("cand-mossa")'
    assert '"id": "cand-mossa"' in llm.system and "CompanyGraph(entityId: string)" in llm.system


async def test_no_visual_when_the_model_declines_or_writes_prose():
    no_sentence = 'root = Answer([g])\ng = CompanyGraph("cand-mossa")'
    for text in ("NONE", "Mossa is great.", no_sentence):
        assert await visual_answer(Stub(text), "hi", PROFILE, fixture_candidates()) is None


async def test_no_visual_without_candidates():
    assert await visual_answer(Stub("root = Answer([])"), "hi", PROFILE, []) is None

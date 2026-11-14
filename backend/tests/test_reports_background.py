import asyncio

from app.llm.fake import FakeLLM
from app.reports import service
from app.store import reports as report_store
from app.store.profile import default_profile


class GatedLLM(FakeLLM):
    """Holds report writing until the test opens the gate."""

    def __init__(self):
        super().__init__()
        self.gate = asyncio.Event()

    async def generate(self, **kwargs):
        await self.gate.wait()
        return await super().generate(**kwargs)


async def test_rebuild_returns_before_the_report_exists_then_stores_it(now, published):
    llm = GatedLLM()
    report_id = service.schedule_rebuild(default_profile(now), llm=llm)

    await asyncio.sleep(0)
    assert report_store.latest() is None

    llm.gate.set()
    await service.wait_idle()
    assert report_store.latest().id == report_id
    assert [kind for kind, _ in published] == ["report"]


async def test_only_the_newest_rebuild_is_stored(now):
    slow, fast = GatedLLM(), FakeLLM()
    first = service.schedule_rebuild(default_profile(now), llm=slow)
    second = service.schedule_rebuild(default_profile(now), llm=fast)
    await asyncio.sleep(0.05)
    slow.gate.set()
    await service.wait_idle()

    assert report_store.latest().id == second
    assert report_store.get(first) is None


async def test_a_failed_rebuild_does_not_break_the_caller(now):
    class Broken(FakeLLM):
        async def generate(self, **kwargs):
            raise RuntimeError("boom")

    service.schedule_rebuild(default_profile(now), llm=Broken())
    await service.wait_idle()
    assert report_store.latest() is None

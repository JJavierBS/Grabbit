import os

os.environ["LLM_MODE"] = "fake"
os.environ["CALA_MODE"] = "replay"
os.environ["GEMINI_API_KEY"] = ""

from datetime import UTC, datetime  # noqa: E402

import pytest  # noqa: E402

from app import events  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.llm import get_llm  # noqa: E402
from app.store import chat as _chat  # noqa: E402, F401
from app.store import db  # noqa: E402
from app.store import profile as _profile  # noqa: E402, F401

NOW = datetime(2026, 11, 14, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    get_settings.cache_clear()
    get_llm.cache_clear()
    events._published.clear()
    db.init_db(str(tmp_path / "test.db"))
    yield
    db.close()


@pytest.fixture
def now():
    return NOW

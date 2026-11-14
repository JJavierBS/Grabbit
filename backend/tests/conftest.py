import json
import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.store.cala_cache import CalaCache

FIXTURES = Path(__file__).parent / "fixtures"


def load_cala(name: str) -> dict:
    return json.loads((FIXTURES / "cala" / f"{name}.json").read_text())


@pytest.fixture(autouse=True)
def offline_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Every test runs offline, on a throwaway database, with demo mode on."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CALA_MODE", "replay")
    monkeypatch.setenv("LLM_MODE", "fake")
    monkeypatch.setenv("DEMO_MODE", "1")
    # A developer's .env may slow walk steps for the demo or ask Gemini for its thoughts.
    monkeypatch.setenv("WALK_STEP_MIN_S", "0")
    monkeypatch.setenv("GEMINI_THOUGHTS", "0")
    get_settings.cache_clear()
    from app.agent.sources import clear_discovery_cache

    clear_discovery_cache()  # in-process event walk: never shared between tests
    yield
    get_settings.cache_clear()
    clear_discovery_cache()


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.main import create_app
    from app.reports.service import wait_idle

    with TestClient(create_app()) as test_client:
        yield test_client
        # Background report rebuilds must finish before the app and its loop shut down.
        test_client.portal.call(wait_idle)


@pytest.fixture(autouse=True)
def agent_db(offline_settings: None) -> Iterator[None]:
    """Agent and report stores on the throwaway database, a fresh FakeLLM per test."""
    from app.context_dev import client as _web  # noqa: F401  registers its cache
    from app.context_dev import get_context_dev
    from app.llm import get_llm
    from app.store import chat, profile, reports  # noqa: F401  registers tables
    from app.store.db import init_db

    get_llm.cache_clear()
    get_context_dev.cache_clear()
    init_db()
    yield
    get_llm.cache_clear()
    get_context_dev.cache_clear()


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 11, 14, 12, 0, tzinfo=UTC)


@pytest.fixture
def published(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, object]]:
    """Events published through `app.events.publish` during the test."""
    from app import events

    seen: list[tuple[str, object]] = []
    original = events.publish

    def record(kind, payload):
        seen.append((kind, payload))
        return original(kind, payload)

    monkeypatch.setattr(events, "publish", record)
    return seen


@pytest.fixture
def conn() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def cache(conn: sqlite3.Connection) -> CalaCache:
    return CalaCache(conn)

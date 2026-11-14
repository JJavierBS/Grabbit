from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings


@pytest.fixture(autouse=True)
def offline_settings(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Every test runs offline, on a throwaway database, with demo mode on."""
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CALA_MODE", "replay")
    monkeypatch.setenv("LLM_MODE", "fake")
    monkeypatch.setenv("DEMO_MODE", "1")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


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

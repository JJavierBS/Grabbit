from collections.abc import Iterator
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

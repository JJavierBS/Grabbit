import json
import sqlite3
from pathlib import Path

import pytest

from app.store.cala_cache import CalaCache

FIXTURES = Path(__file__).parent / "fixtures"


def load_cala(name: str) -> dict:
    return json.loads((FIXTURES / "cala" / f"{name}.json").read_text())


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def cache(conn):
    return CalaCache(conn)

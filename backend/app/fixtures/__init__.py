"""Fixture data behind the mock endpoints and the frontend tests (api.md "mock")."""

import json
from functools import cache
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from app.models import Alert, ChatMessage, Profile, ProfileChange, Report

FIXTURES_DIR = Path(__file__).parent
DEMO_EVENTS_DIR = FIXTURES_DIR / "demo_events"


@cache
def _read(relative_path: str) -> str:
    return (FIXTURES_DIR / relative_path).read_text(encoding="utf-8")


def load_json(relative_path: str) -> Any:
    """Fresh parsed copy of a fixture file, safe to mutate."""
    return json.loads(_read(relative_path))


def profile() -> Profile:
    return Profile.model_validate(load_json("profile.json"))


def profile_history() -> list[ProfileChange]:
    return TypeAdapter(list[ProfileChange]).validate_python(load_json("profile_history.json"))


def chat() -> list[ChatMessage]:
    return TypeAdapter(list[ChatMessage]).validate_python(load_json("chat.json"))


def latest_report() -> Report:
    return Report.model_validate(load_json("report_latest.json"))


def alerts() -> list[Alert]:
    return TypeAdapter(list[Alert]).validate_python(load_json("alerts.json"))


def demo_event_names() -> list[str]:
    return sorted(path.stem for path in DEMO_EVENTS_DIR.glob("*.json"))


def demo_event(name: str) -> dict[str, Any] | None:
    if name not in demo_event_names():
        return None
    return load_json(f"demo_events/{name}.json")

"""Settings read from the environment and the repo-root `.env` (see `.env.example`)."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.models import CalaMode, LLMMode

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    cala_api_key: str = ""
    context_dev_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = ""
    gemini_timeout_s: float = 30.0
    gemini_thoughts: bool = False
    walk_step_min_s: float = 0.0
    cala_mode: CalaMode = "live"
    # One Cala request at a time for the whole process, starts this far apart (#119).
    cala_max_concurrency: int = 1
    cala_min_interval_ms: int = 250
    llm_mode: LLMMode = "gemini"
    demo_mode: bool = False
    database_path: Path = Path("data/grabbit.db")

    @property
    def database_file(self) -> Path:
        """`DATABASE_PATH` resolved against the repo root when relative."""
        path = self.database_path
        return path if path.is_absolute() else REPO_ROOT / path


@lru_cache
def get_settings() -> Settings:
    return Settings()

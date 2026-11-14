from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cala_api_key: str = ""
    cala_mode: Literal["live", "replay"] = "live"
    context_dev_api_key: str = ""
    gemini_api_key: str = ""
    gemini_model: str = ""
    gemini_timeout_s: float = 30.0
    llm_mode: Literal["gemini", "fake"] = "gemini"
    demo_mode: bool = False
    database_path: str = "data/grabbit.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()

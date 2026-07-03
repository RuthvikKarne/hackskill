"""AI Engine configuration via environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIEngineSettings(BaseSettings):
    """AI Engine settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "HRIP AI Engine"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"

    # ── Database (read-only connection) ───────────────────────────────────────
    DATABASE_URL: PostgresDsn

    # ── Authentication ────────────────────────────────────────────────────────
    # API key required for backend → AI engine calls
    API_KEY: str

    # ── Model Configuration ───────────────────────────────────────────────────
    MODEL_PATH: str = "/app/models"

    # ── Backend ───────────────────────────────────────────────────────────────
    # URL of the backend to write recommendations
    BACKEND_URL: str = "http://backend:8000"


@lru_cache
def get_settings() -> AIEngineSettings:
    """Return cached AI engine settings."""
    return AIEngineSettings()  # type: ignore[call-arg]

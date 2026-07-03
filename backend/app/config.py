"""Application configuration via environment variables.

All configuration is sourced from environment variables.
Sensitive values (secrets, keys) must never have defaults.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Application ────────────────────────────────────────────────────────────
    APP_NAME: str = "HRIP Backend"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ──────────────────────────────────────────────────────────────────
    REDIS_URL: RedisDsn

    # ── JWT ────────────────────────────────────────────────────────────────────
    # RS256 — use private/public key pair in production
    JWT_PRIVATE_KEY: str  # PEM-encoded RSA private key
    JWT_PUBLIC_KEY: str   # PEM-encoded RSA public key
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "RS256"

    # ── Security ───────────────────────────────────────────────────────────────
    CORS_ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 300

    # ── AI Engine ──────────────────────────────────────────────────────────────
    AI_ENGINE_URL: str = "http://ai-engine:8001"
    AI_ENGINE_API_KEY: str

    # ── Supabase Storage ───────────────────────────────────────────────────────
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "medical-files"

    # ── Notifications ──────────────────────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMS_GATEWAY_URL: str = ""
    SMS_GATEWAY_KEY: str = ""

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Ensure environment is a known value."""
        allowed = {"development", "staging", "production"}
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings.

    Using lru_cache ensures environment variables are read once
    and the Settings object is reused across all requests.
    """
    return Settings()  # type: ignore[call-arg]

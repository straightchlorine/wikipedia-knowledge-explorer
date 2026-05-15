"""Typed application configuration.

Loaded once via `get_settings()` (LRU-cached). All env vars are typed and
validated by Pydantic. Adding a new env var means adding a field here;
unset required vars fail loudly at boot rather than later at use.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field, RedisDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    wikipedia_api_url: AnyHttpUrl = Field(
        ...,
        description="Wikipedia REST API endpoint (no trailing slash on path).",
    )

    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        description=(
            "Allowed CORS origins. Defaults to empty list (closed). "
            "Provide as a comma-separated string in the env var."
        ),
    )

    summarizer_url: AnyHttpUrl | None = Field(
        default=None,
        description=(
            "Base URL of the wke-summarizer inference service. "
            "If unset, the in-API TFIDFSummarizer fallback is used."
        ),
    )
    summarizer_timeout_seconds: float = Field(
        default=30.0,
        description="Per-request timeout to the summarizer service.",
    )
    summarizer_max_concurrency: int = Field(
        default=8,
        ge=1,
        description="Semaphore size for fan-out to the summarizer service.",
    )

    redis_url: RedisDsn | None = Field(
        default=None,
        description="Optional Redis cache URL for summary results.",
    )

    summarizer_model: str = Field(
        default="sshleifer/distilbart-cnn-6-6",
        description="HuggingFace model name used by the summarizer service.",
    )
    summarizer_model_revision: str | None = Field(
        default=None,
        description=(
            "HF model revision (commit SHA). Required if SUMMARIZER_URL is set "
            "for supply-chain integrity — fail-closed otherwise."
        ),
    )
    summarizer_cache_ttl_seconds: int = Field(
        default=2_592_000,
        ge=0,
        description="Redis TTL for cached summaries (default 30 days).",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: object) -> object:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _require_revision_when_summarizer_enabled(self) -> Settings:
        if self.summarizer_url is not None and not self.summarizer_model_revision:
            raise ValueError(
                "SUMMARIZER_MODEL_REVISION must be set when SUMMARIZER_URL is "
                "configured (supply-chain integrity)."
            )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

"""Configuration for the summarizer inference service.

Read from environment.

The model identity (name + revision) is required:
the image is built against a specific commit hash, and the running container
must echo that revision in every SummarizeResponse for cache-key + audit purposes.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    summarizer_model: str = Field(
        default="sshleifer/distilbart-cnn-6-6",
        description="HuggingFace model id used by the pipeline.",
    )
    summarizer_model_revision: str = Field(
        ...,
        description="HuggingFace model revision (commit SHA)."
        + "Required - pinned at image build time.",
    )

    max_input_length: int = Field(default=1024, ge=64, le=4096)
    max_output_length: int = Field(default=130, ge=10, le=512)
    min_output_length: int = Field(default=30, ge=1, le=256)

    rate_limit_per_minute: int = Field(default=60, ge=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

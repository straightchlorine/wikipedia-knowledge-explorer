"""Tests for the typed settings module.

`get_settings()` is `lru_cache`d, so we clear the cache between tests that
mutate the env to avoid leaking state.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from wiki.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def _reset_settings_cache(monkeypatch: pytest.MonkeyPatch):
    """Reset the lru_cache and isolate env per test."""
    # Ensure no .env on disk leaks in, by pointing pydantic-settings at a path
    # that doesn't exist. Tests provide their own env vars via monkeypatch.
    original_env_file = Settings.model_config.get("env_file")
    Settings.model_config["env_file"] = "/nonexistent/.env"
    get_settings.cache_clear()
    try:
        yield
    finally:
        Settings.model_config["env_file"] = original_env_file
        get_settings.cache_clear()


def test_get_settings_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")

    first = get_settings()
    second = get_settings()

    assert first is second


def test_missing_required_var_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WIKIPEDIA_API_URL", raising=False)

    with pytest.raises(ValidationError):
        Settings()


def test_cors_origins_parses_comma_separated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "http://localhost:5173, http://127.0.0.1:5173 ,https://wke.example.com",
    )

    s = Settings()

    assert s.cors_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://wke.example.com",
    ]


def test_cors_origins_defaults_to_empty_list(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    s = Settings()

    assert s.cors_origins == []


def test_summarizer_url_without_revision_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    monkeypatch.setenv("SUMMARIZER_URL", "http://wke-summarizer:8000")
    monkeypatch.delenv("SUMMARIZER_MODEL_REVISION", raising=False)

    with pytest.raises(ValidationError):
        Settings()


def test_summarizer_url_with_revision_validates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    monkeypatch.setenv("SUMMARIZER_URL", "http://wke-summarizer:8000")
    monkeypatch.setenv("SUMMARIZER_MODEL_REVISION", "abc123def456")

    s = Settings()

    assert str(s.summarizer_url).startswith("http://wke-summarizer:8000")
    assert s.summarizer_model_revision == "abc123def456"


def test_summarizer_url_unset_is_fine_without_revision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    monkeypatch.delenv("SUMMARIZER_URL", raising=False)
    monkeypatch.delenv("SUMMARIZER_MODEL_REVISION", raising=False)

    s = Settings()

    assert s.summarizer_url is None
    assert s.summarizer_model_revision is None

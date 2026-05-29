"""Shared fixtures.

The HuggingFace seq2seq backend is replaced by a stub across every test:
real loading downloads ~300 MB of weights and takes 60 s on a cold cache,
neither of which is acceptable in a unit suite. We inject a stub backend
through ModelHolder's constructor seam (see app/model.py:BackendFactory).
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("SUMMARIZER_MODEL_REVISION", "test-revision-sha")


class StubBackend:
    """In-memory stand-in for `_HfSeq2SeqBackend` — counts calls + returns
    a deterministic string. Tests can read `call_count` and `last_call`."""

    def __init__(self, summary: str = "mocked summary") -> None:
        self._summary = summary
        self.call_count = 0
        self.last_call: dict[str, object] | None = None

    def summarize(self, text: str, max_length: int, min_length: int) -> str:
        self.call_count += 1
        self.last_call = {
            "text": text,
            "max_length": max_length,
            "min_length": min_length,
        }
        return self._summary


@pytest.fixture
def stub_backend() -> StubBackend:
    return StubBackend()


@pytest.fixture
def backend_factory(stub_backend: StubBackend):
    """Drop-in replacement for `_default_backend_factory` in ModelHolder."""

    def _factory(model: str, revision: str, max_input_length: int) -> StubBackend:
        return stub_backend

    return _factory


@pytest.fixture
def reset_settings_cache() -> None:
    from app.settings import get_settings

    get_settings.cache_clear()



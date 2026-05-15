"""End-to-end tests for the summarizer HTTP surface.

The seq2seq backend is replaced via a constructor seam on ModelHolder
(see conftest.StubBackend / backend_factory) — these tests exercise
the FastAPI shell (lifespan, validation, probes) without ever touching
real model weights.
"""

from __future__ import annotations

from typing import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.model import BackendFactory
from app.settings import get_settings
from tests.conftest import StubBackend


@pytest.fixture
def client(
    backend_factory: BackendFactory,
    reset_settings_cache: None,
) -> Iterator[TestClient]:
    app = create_app(backend_factory=backend_factory)
    with TestClient(app) as test_client:
        yield test_client


def test_summarize_returns_string(client: TestClient) -> None:
    response = client.post(
        "/summarize",
        json={"text": "Some article text to summarize.", "max_length": 50, "min_length": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == "mocked summary"
    assert body["model"] == get_settings().summarizer_model
    assert body["revision"] == get_settings().summarizer_model_revision


def test_input_validation_too_long(client: TestClient) -> None:
    response = client.post("/summarize", json={"text": "x" * 100_000})
    assert response.status_code == 422


def test_input_validation_empty(client: TestClient) -> None:
    response = client.post("/summarize", json={"text": ""})
    assert response.status_code == 422


def test_input_validation_max_length_too_small(client: TestClient) -> None:
    response = client.post("/summarize", json={"text": "hi", "max_length": 5})
    assert response.status_code == 422


def test_healthz_before_model_loaded(
    backend_factory: BackendFactory,
    reset_settings_cache: None,
) -> None:
    """Build the TestClient *without* entering its context — the lifespan
    hasn't run, so the model is not yet loaded. /healthz must return 503.
    """
    app = create_app(backend_factory=backend_factory)
    test_client = TestClient(app, raise_server_exceptions=False)
    response = test_client.get("/healthz")
    assert response.status_code == 503


def test_readyz_after_warmup(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_healthz_after_load(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_warmup_invokes_backend(
    backend_factory: BackendFactory,
    stub_backend: StubBackend,
    reset_settings_cache: None,
) -> None:
    """Lifespan must perform at least one warmup inference before flipping
    ready; after context exit the stub has seen >= 1 call."""
    app = create_app(backend_factory=backend_factory)
    with TestClient(app):
        pass
    assert stub_backend.call_count >= 1


def test_summary_response_echoes_model_identity(client: TestClient) -> None:
    response = client.post("/summarize", json={"text": "Some article text."})
    body = response.json()
    settings = get_settings()
    assert body["model"] == settings.summarizer_model
    assert body["revision"] == settings.summarizer_model_revision


def test_backend_receives_request_params(
    client: TestClient,
    stub_backend: StubBackend,
) -> None:
    """Verify max_length / min_length from the request reach the backend."""
    client.post(
        "/summarize",
        json={"text": "Some article text.", "max_length": 75, "min_length": 25},
    )
    assert stub_backend.last_call is not None
    assert stub_backend.last_call["max_length"] == 75
    assert stub_backend.last_call["min_length"] == 25

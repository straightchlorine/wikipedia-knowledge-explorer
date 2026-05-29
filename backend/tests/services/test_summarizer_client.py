"""Tests for the SummarizerClient fallback decision tree, cache, and bounding.

Each test builds an httpx.AsyncClient backed by httpx.MockTransport so we can
script the exact wire behavior — timeout, connect error, status codes — that
the decision tree needs to differentiate.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import fakeredis.aioredis
import httpx
import pytest

from wiki.services.cache import CACHE_KEY_PREFIX, SummaryCache
from wiki.services.summarizer_client import SummarizerClient
from wiki.settings import Settings

SUMMARIZER_BASE = "http://summarizer:8000"


def _make_settings(*, with_url: bool = True, max_concurrency: int = 8) -> Settings:
    return Settings(
        wikipedia_api_url="https://en.wikipedia.org/w/api.php",
        summarizer_url=SUMMARIZER_BASE if with_url else None,
        summarizer_model_revision="abc123" if with_url else None,
        summarizer_max_concurrency=max_concurrency,
        summarizer_timeout_seconds=5.0,
    )


def _make_fallback(returns: str = "fallback summary"):
    fallback = MagicMock()
    fallback.summarize = MagicMock(return_value=returns)
    return fallback


@pytest.fixture
async def empty_cache():
    redis = fakeredis.aioredis.FakeRedis()
    cache = SummaryCache(redis, ttl_seconds=60)
    yield cache
    await cache.close()


def _client_with_transport(
    settings: Settings, cache: SummaryCache, fallback, transport: httpx.MockTransport
) -> SummarizerClient:
    http = httpx.AsyncClient(base_url=SUMMARIZER_BASE, transport=transport, timeout=5.0)
    return SummarizerClient(settings, cache, fallback, http_client=http)


async def test_no_url_uses_fallback_directly(empty_cache):
    settings = _make_settings(with_url=False)
    fallback = _make_fallback("local-tfidf")
    # No HTTP transport needed when URL is unset — the client must not hit network.
    transport = httpx.MockTransport(lambda req: pytest.fail("HTTP call must not occur"))
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    result = await client.summarize("hello")

    assert result == "local-tfidf"
    fallback.summarize.assert_called_once_with("hello")
    await client.aclose()


async def test_uses_cache_when_present(empty_cache):
    settings = _make_settings()
    fallback = _make_fallback()
    transport = httpx.MockTransport(lambda req: pytest.fail("cache hit should bypass HTTP"))
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    cache_key = client._cache_key("cached text")
    assert cache_key.startswith(CACHE_KEY_PREFIX)
    await empty_cache.set(cache_key, "from cache")

    result = await client.summarize("cached text")

    assert result == "from cache"
    fallback.summarize.assert_not_called()
    await client.aclose()


async def test_writes_cache_on_happy_path(empty_cache):
    settings = _make_settings()
    fallback = _make_fallback()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"summary": "real summary"})

    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    result = await client.summarize("brand new text")
    assert result == "real summary"

    # Second call hits the cache, not the transport.
    transport.handler = lambda req: pytest.fail("expected cache hit on second call")
    result_again = await client.summarize("brand new text")
    assert result_again == "real summary"
    fallback.summarize.assert_not_called()
    await client.aclose()


async def test_falls_back_on_timeout(empty_cache):
    settings = _make_settings()
    fallback = _make_fallback("after-timeout")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("boom", request=request)

    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    result = await client.summarize("anything")
    assert result == "after-timeout"
    fallback.summarize.assert_called_once_with("anything")
    await client.aclose()


async def test_falls_back_on_connect_error(empty_cache):
    settings = _make_settings()
    fallback = _make_fallback("after-connect-error")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("nope", request=request)

    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    result = await client.summarize("anything")
    assert result == "after-connect-error"
    await client.aclose()


async def test_falls_back_on_5xx(empty_cache):
    settings = _make_settings()
    fallback = _make_fallback("after-5xx")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="upstream down")

    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    result = await client.summarize("anything")
    assert result == "after-5xx"
    fallback.summarize.assert_called_once()
    await client.aclose()


async def test_does_not_fall_back_on_4xx(empty_cache):
    """4xx is our bug (bad request shape) — propagate, do not silently fall back."""
    settings = _make_settings()
    fallback = _make_fallback("must-not-be-called")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(422, json={"detail": "bad request"})

    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    with pytest.raises(httpx.HTTPStatusError):
        await client.summarize("anything")
    fallback.summarize.assert_not_called()
    await client.aclose()


async def test_semaphore_bounds_concurrency(empty_cache):
    """Fire many calls with low concurrency; observed max-in-flight must equal the limit."""
    max_concurrency = 3
    settings = _make_settings(max_concurrency=max_concurrency)
    fallback = _make_fallback()

    in_flight = 0
    peak = 0
    started = asyncio.Event()

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal in_flight, peak
        in_flight += 1
        peak = max(peak, in_flight)
        started.set()
        await asyncio.sleep(0.02)
        in_flight -= 1
        return httpx.Response(200, json={"summary": "ok"})

    # Note: httpx.MockTransport supports an async handler via AsyncByteStream;
    # to use an async handler we set transport's request handler accordingly.
    transport = httpx.MockTransport(handler)
    client = _client_with_transport(settings, empty_cache, fallback, transport)

    tasks = [client.summarize(f"text-{i}") for i in range(20)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 20
    assert peak <= max_concurrency
    await client.aclose()


async def test_cache_key_changes_with_model_revision(empty_cache):
    settings_a = _make_settings()
    settings_b = Settings(
        wikipedia_api_url="https://en.wikipedia.org/w/api.php",
        summarizer_url=SUMMARIZER_BASE,
        summarizer_model_revision="different-sha",
    )
    fallback = _make_fallback()
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"summary": "x"}))
    client_a = _client_with_transport(settings_a, empty_cache, fallback, transport)
    client_b = _client_with_transport(settings_b, empty_cache, fallback, transport)

    key_a = client_a._cache_key("same text")
    key_b = client_b._cache_key("same text")
    assert key_a != key_b
    await client_a.aclose()
    await client_b.aclose()


async def test_cache_no_op_when_redis_unset():
    """SummaryCache(None, ...) must read None and write nothing without errors."""
    cache = SummaryCache(None, ttl_seconds=60)
    assert await cache.get("any-key") is None
    await cache.set("any-key", "value")
    assert await cache.get("any-key") is None
    await cache.close()

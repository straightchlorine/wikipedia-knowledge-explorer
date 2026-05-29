"""HTTP client to the wke-summarizer inference service with cache + fallback.

Decision tree (per REVIEW_backend.md § A1.5):

    summarize(text)
      cache hit?                                 -> return cached
      SUMMARIZER_URL unset?                      -> TFIDFSummarizer fallback
      POST /summarize 200 OK                     -> return summary, cache it
      POST /summarize Timeout/ConnectError/5xx   -> TFIDFSummarizer fallback
                                                    + wke_summary_fallback_total++
      POST /summarize 4xx                        -> re-raise (our bug, not theirs)

A 4xx is treated as a programming error in the caller (request shape wrong)
and propagated to the unhandled-exception handler. Operational degradation
(timeout, connect error, 5xx) is absorbed via the TF-IDF fallback so the
endpoint stays responsive while ops follows the Prometheus alert.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging

import httpx
from prometheus_client import Counter

from wiki.processors.text.summarizers.summarizer import TextSummarizer
from wiki.services.cache import CACHE_KEY_PREFIX, SummaryCache
from wiki.settings import Settings

logger = logging.getLogger(__name__)

summary_fallback_total = Counter(
    "wke_summary_fallback_total",
    "Number of summarize() calls that fell back to TFIDFSummarizer.",
    ["reason"],
)


class SummarizerClient:
    def __init__(
        self,
        settings: Settings,
        cache: SummaryCache,
        fallback: TextSummarizer,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._settings = settings
        self._cache = cache
        self._fallback = fallback
        if http_client is not None:
            self._http = http_client
            self._owns_http = False
        else:
            self._http = httpx.AsyncClient(
                base_url=str(settings.summarizer_url) if settings.summarizer_url else "",
                timeout=settings.summarizer_timeout_seconds,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
            )
            self._owns_http = True
        self._semaphore = asyncio.Semaphore(settings.summarizer_max_concurrency)

    async def summarize(self, text: str) -> str:
        cache_key = self._cache_key(text)
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return cached

        async with self._semaphore:
            summary = await self._summarize_with_fallback(text)

        await self._cache.set(cache_key, summary)
        return summary

    async def _summarize_with_fallback(self, text: str) -> str:
        if self._settings.summarizer_url is None:
            return self._fallback.summarize(text)
        try:
            response = await self._http.post("/summarize", json={"text": text})
            response.raise_for_status()
        except httpx.TimeoutException:
            logger.warning("summarizer timeout; falling back to TF-IDF")
            summary_fallback_total.labels(reason="timeout").inc()
            return self._fallback.summarize(text)
        except httpx.ConnectError:
            logger.warning("summarizer unreachable; falling back to TF-IDF")
            summary_fallback_total.labels(reason="connect_error").inc()
            return self._fallback.summarize(text)
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            # 429 is operational degradation, not a request-shape bug: the API
            # pod and summarizer share a get_ipaddr bucket, so absorb it as a
            # transient. 5xx is the usual fallback case (incl. 503 cold start).
            if status == 429 or status >= 500:
                logger.warning("summarizer %s; falling back to TF-IDF", status)
                summary_fallback_total.labels(reason=f"http_{status}").inc()
                return self._fallback.summarize(text)
            # Other 4xx — our request shape is wrong; propagate so it surfaces.
            raise
        return response.json()["summary"]

    def _cache_key(self, text: str) -> str:
        model = self._settings.summarizer_model
        # Empty-string revision is fine for cache hashing — it just means the
        # fallback is the only path (no SUMMARIZER_URL). Settings already
        # enforces that revision is set when SUMMARIZER_URL is.
        revision = self._settings.summarizer_model_revision or ""
        payload = f"{text}|{model}@{revision}".encode("utf-8")
        return f"{CACHE_KEY_PREFIX}{hashlib.sha256(payload).hexdigest()}"

    async def aclose(self) -> None:
        if self._owns_http:
            await self._http.aclose()

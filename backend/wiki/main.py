import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from redis.asyncio import Redis
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException

from wiki.limits import limiter
from wiki.processors.text.summarizers.tf_idf_summarizer import TFIDFSummarizer
from wiki.routes import articles
from wiki.services import wikipedia_fetcher
from wiki.services.cache import SummaryCache
from wiki.services.summarizer_client import SummarizerClient
from wiki.settings import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Construct and tear down shared service clients.

    Owns: shared httpx client (used by both wikipedia_fetcher and the
    SummarizerClient), optional async Redis connection, SummaryCache (no-op
    when Redis is unset), and SummarizerClient. The TFIDFSummarizer is the
    in-API fallback when SUMMARIZER_URL is unset or the service is degraded.

    Teardown order is the reverse of construction so dependents close first.
    """
    settings = get_settings()

    wiki_http_client = httpx.AsyncClient(
        timeout=15.0,
        headers={
            # Wikipedia's API rejects requests without an identifying UA per
            # https://wikitech.wikimedia.org/wiki/Robot_policy. Include a
            # contact so abuse can be diagnosed before a blanket block.
            "User-Agent": (
                "wke/0.1 (+https://github.com/straightchlorine/"
                "wikipedia-knowledge-explorer)"
            ),
        },
    )
    wikipedia_fetcher.set_client(wiki_http_client)

    redis: Redis | None = None
    if settings.redis_url is not None:
        redis = Redis.from_url(str(settings.redis_url))

    cache = SummaryCache(redis, settings.summarizer_cache_ttl_seconds)
    fallback = TFIDFSummarizer()
    summarizer = SummarizerClient(settings, cache, fallback)
    app.state.summarizer = summarizer

    try:
        yield
    finally:
        await summarizer.aclose()
        await cache.close()
        await wiki_http_client.aclose()
        wikipedia_fetcher.set_client(None)


settings = get_settings()

wiki_exp = FastAPI(lifespan=lifespan)

wiki_exp.state.limiter = limiter
wiki_exp.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@wiki_exp.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Map any uncaught exception to a generic 500 to avoid error-message leakage."""
    if isinstance(exc, (HTTPException, StarletteHTTPException)):
        raise exc
    # Log path only — never request.url (would include query string with user input)
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@wiki_exp.middleware("http")
async def security_headers(request: Request, call_next) -> Response:
    """Set baseline security response headers on every response.

    - HSTS: force HTTPS for the year following the response (ingress already
      terminates TLS — this hardens the user agent).
    - X-Content-Type-Options: nosniff prevents MIME sniffing.
    - Referrer-Policy: strict-origin-when-cross-origin avoids leaking paths.
    - Permissions-Policy: () disables all browser features by default.
    """
    response: Response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "()"
    return response


wiki_exp.include_router(articles.router, prefix="/api")

wiki_exp.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["content-type"],
)


@wiki_exp.get("/")
def read_root():
    return {"message": "Wikipedia Knowledge Explorer API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(wiki_exp)

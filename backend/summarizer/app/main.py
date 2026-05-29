"""FastAPI entrypoint for the summarizer service.

Endpoints:
  POST /summarize  — wire protocol
  GET  /healthz    — 200 once weights are resident in memory
  GET  /readyz     — 200 once /healthz AND a warmup inference has run

Rate limiting via slowapi (single Limiter instance shared with the
exception handler — same pattern as wiki/limits.py in the API pod).
The lifespan loads weights synchronously on startup; Kubernetes won't
send traffic until /readyz returns 200, which the readinessProbe gates.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_ipaddr

from app.model import BackendFactory, ModelHolder
from app.schemas import SummarizeRequest, SummarizeResponse
from app.settings import get_settings

logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_ipaddr)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    holder: ModelHolder = app.state.model
    settings = app.state.settings
    try:
        holder.load()
        holder.summarize(
            "Warm up text for the summarization pipeline.",
            max_length=settings.max_output_length,
            min_length=settings.min_output_length,
        )
        holder.mark_ready()
        logger.info("Summarizer ready")
    except Exception:
        logger.exception("Failed to warm summarizer model")
    yield


def create_app(backend_factory: BackendFactory | None = None) -> FastAPI:
    app = FastAPI(title="wke-summarizer", lifespan=lifespan)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_handler)

    settings = get_settings()
    app.state.settings = settings
    holder_kwargs: dict[str, Any] = {"max_input_length": settings.max_input_length}
    if backend_factory is not None:
        holder_kwargs["backend_factory"] = backend_factory
    app.state.model = ModelHolder(
        settings.summarizer_model,
        settings.summarizer_model_revision,
        **holder_kwargs,
    )

    rate = f"{settings.rate_limit_per_minute}/minute"

    @app.post("/summarize", response_model=SummarizeResponse)
    @limiter.limit(rate)
    async def summarize(request: Request, body: SummarizeRequest) -> SummarizeResponse:
        holder: ModelHolder = request.app.state.model
        if not holder.is_ready:
            raise HTTPException(status_code=503, detail="Model not ready")
        summary = holder.summarize(
            body.text,
            max_length=body.max_length,
            min_length=body.min_length,
        )
        return SummarizeResponse(
            summary=summary,
            model=holder.model,
            revision=holder.revision,
        )

    @app.get("/healthz")
    async def healthz(request: Request) -> JSONResponse:
        holder: ModelHolder = request.app.state.model
        if not holder.is_loaded:
            return JSONResponse(status_code=503, content={"status": "loading"})
        return JSONResponse(status_code=200, content={"status": "ok"})

    @app.get("/readyz")
    async def readyz(request: Request) -> JSONResponse:
        holder: ModelHolder = request.app.state.model
        if not holder.is_ready:
            return JSONResponse(status_code=503, content={"status": "warming"})
        return JSONResponse(status_code=200, content={"status": "ready"})

    return app


async def _rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"},
    )


app = create_app()

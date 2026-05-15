FROM python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664 AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip wheel

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim@sha256:d168b8d9eb761f4d3fe305ebd04aeb7e7f2de0297cec5fb2f8f6403244621664 AS runtime

LABEL org.opencontainers.image.source="https://github.com/straightchlorine/wikipedia-knowledge-explorer"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="wke-backend"
LABEL org.opencontainers.image.description="Wikipedia Knowledge Explorer — FastAPI backend"

RUN groupadd -r --gid 1000 appuser && useradd -r --uid 1000 --gid 1000 -d /home/appuser -m appuser

WORKDIR /app

COPY --from=builder /install /usr/local

USER appuser

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/docs').read()" || exit 1

CMD ["uvicorn", "wiki.main:wiki_exp", "--host", "0.0.0.0", "--port", "8000"]

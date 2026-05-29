# Multi-stage build for the wke-summarizer service.
#
# Model weights are pre-baked into the image during the builder stage
# so runtime pods boot in seconds.
# The revision is required at build time - without it, the build fails.
#
# Look up the current pin via:
#   curl -s https://huggingface.co/api/models/sshleifer/distilbart-cnn-6-6 | jq -r .sha
# and pass it as `--build-arg SUMMARIZER_MODEL_REVISION=<sha>`.
#
# Multi-arch (linux/amd64 + linux/arm64) is the infra-builder's
# concern via `docker buildx`; this file targets either platform.

ARG PYTHON_BASE=python:3.13-slim@sha256:dc1546eefcbe8caaa1f004f16ab76b204b5e1dbd58ff81b899f21cd40541232f

FROM ${PYTHON_BASE} AS builder

ARG SUMMARIZER_MODEL=sshleifer/distilbart-cnn-6-6
ARG SUMMARIZER_MODEL_REVISION
RUN test -n "${SUMMARIZER_MODEL_REVISION}" || (echo "SUMMARIZER_MODEL_REVISION build-arg is required" && exit 1)

ENV HF_HOME=/opt/hf-cache \
    TRANSFORMERS_CACHE=/opt/hf-cache \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

COPY --from=ghcr.io/astral-sh/uv:0.11.14@sha256:1025398289b62de8269e70c45b91ffa37c373f38118d7da036fb8bb8efc85d97 /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --no-emit-project -o /tmp/requirements.txt \
    && uv pip install --system --prefix=/install \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        -r /tmp/requirements.txt

# Pre-bake model weights so runtime pods skip the cold download.
# Transformers 5.x dropped the `pipeline("summarization", ...)` shortcut.
# Load via AutoTokenizer + AutoModelForSeq2SeqLM directly - same
# shape used by app/model.py:_HfSeq2SeqBackend.
RUN PYTHONPATH=/install/lib/python3.13/site-packages python -c "\
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
AutoTokenizer.from_pretrained('${SUMMARIZER_MODEL}', revision='${SUMMARIZER_MODEL_REVISION}'); \
AutoModelForSeq2SeqLM.from_pretrained('${SUMMARIZER_MODEL}', revision='${SUMMARIZER_MODEL_REVISION}')"

FROM ${PYTHON_BASE} AS runtime

LABEL org.opencontainers.image.source="https://github.com/straightchlorine/wikipedia-knowledge-explorer"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.title="wke-summarizer"
LABEL org.opencontainers.image.description="Wikipedia Knowledge Explorer - summarization inference service"

ARG SUMMARIZER_MODEL=sshleifer/distilbart-cnn-6-6
ARG SUMMARIZER_MODEL_REVISION
RUN test -n "${SUMMARIZER_MODEL_REVISION}" || (echo "SUMMARIZER_MODEL_REVISION build-arg is required" && exit 1)

RUN groupadd -r --gid 1000 appuser \
    && useradd -r --uid 1000 --gid 1000 -d /home/appuser -m appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder --chown=appuser:appuser /opt/hf-cache /opt/hf-cache

COPY --chown=appuser:appuser app/ ./app/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    HF_HOME=/opt/hf-cache \
    TRANSFORMERS_CACHE=/opt/hf-cache \
    SUMMARIZER_MODEL=${SUMMARIZER_MODEL} \
    SUMMARIZER_MODEL_REVISION=${SUMMARIZER_MODEL_REVISION}

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request, sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/healthz').status == 200 else 1)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

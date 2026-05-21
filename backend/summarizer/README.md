# wke-summarizer

Standalone FastAPI inference service that fronts a HuggingFace
`summarization` pipeline. The API pod (`backend/wiki/`) calls
`POST /summarize` over the cluster network; this service owns the
ML deps (`torch`, `transformers`) so the API image stays slim.

## Wire protocol

`POST /summarize`

Request:

```json
{ "text": "...", "max_length": 130, "min_length": 30 }
```

Response:

```json
{ "summary": "...", "model": "sshleifer/distilbart-cnn-6-6", "revision": "<commit-sha>" }
```

The `revision` echoed in every response is the pinned HuggingFace
commit SHA — the API pod uses `f"{model}@{revision}"` as part of the
Redis cache key so a model rev change invalidates the cache cleanly.

Probes:

- `GET /healthz` — 200 once model weights are resident in memory.
- `GET /readyz` — 200 once `/healthz` is true AND a warmup inference
  has succeeded. Use this as the Kubernetes readinessProbe.

Rate limit: 60/min per client IP on `POST /summarize` (slowapi,
`get_ipaddr` so `X-Forwarded-For` is honored — requires
`uvicorn --proxy-headers --forwarded-allow-ips=<cidr>` in the pod
spec).

## Pinned model revision

`sshleifer/distilbart-cnn-6-6` is pinned to commit
`d2fde4ca965ba893255479612e4b801aa6500029`
(looked up 2026-05-15 via the HF API). Refresh with:

```bash
curl -s https://huggingface.co/api/models/sshleifer/distilbart-cnn-6-6 \
  | jq -r .sha
```

This SHA must be passed both at build time (`--build-arg
SUMMARIZER_MODEL_REVISION=...`, which gates the weight pre-bake step)
and at runtime via the `SUMMARIZER_MODEL_REVISION` env var, which
the `wke-config` ConfigMap supplies in the deployed cluster.

## Local development

```bash
cd backend/summarizer
uv sync
SUMMARIZER_MODEL_REVISION=d2fde4ca965ba893255479612e4b801aa6500029 \
  uv run uvicorn app.main:app --reload --port 8001
```

The first start downloads weights (~300 MB) into `$HF_HOME` —
subsequent starts hit the cache.

## Tests

```bash
cd backend/summarizer
uv run pytest -q
```

Tests mock `transformers.pipeline`, so no network or weights are
needed.

## Container build

```bash
cd backend/summarizer
docker build \
  --build-arg SUMMARIZER_MODEL_REVISION=d2fde4ca965ba893255479612e4b801aa6500029 \
  -t wke-summarizer:test .
```

The build downloads weights inside the builder stage and copies the
HF cache into the runtime stage. Pods skip the cold-load.

Multi-arch (amd64 + arm64) is the infra-builder's concern, driven via
`docker buildx`. The Dockerfile itself takes no `--platform` flag.

## Notes

- transformers 5.x removed the `pipeline("summarization", ...)` shortcut;
  we drive `AutoTokenizer` + `AutoModelForSeq2SeqLM` directly. See
  `app/model.py:_HfSeq2SeqBackend`.
- torch is installed CPU-only (`torch==2.11.0+cpu` from the PyTorch
  CPU index). Infrastructure concern.
- The `BackendFactory` seam in `app/model.py` is what makes the
  test suite reliable. The real `transformers` package ships as a
  `_LazyModule` whose attribute mutation swaps `sys.modules` entries,
  so naive `monkeypatch.setattr("transformers.pipeline", ...)` is
  unreliable. Inject the backend factory through the constructor
  instead.

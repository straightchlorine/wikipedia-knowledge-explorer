"""ModelHolder — lazy-loaded HuggingFace summarization pipeline singleton.

is_loaded flips true after `load()` returns; is_ready flips true after
a warmup inference has completed successfully. The health probe gates
on is_loaded; the readiness probe gates on is_ready. This matches the
two-probe pattern documented in REVIEW_backend.md A1.4.

Loading happens inside a threading.Lock so the FastAPI lifespan can
call load() concurrently with no risk of building two pipelines.
"""

from __future__ import annotations

import logging
import threading
from typing import Any, Callable, Protocol

logger = logging.getLogger(__name__)


class SummarizationBackend(Protocol):
    """A thin object that can turn text into a summary string.

    Required because transformers 5.x dropped the `pipeline("summarization", ...)`
    shortcut — we drive `AutoModelForSeq2SeqLM` + `AutoTokenizer` directly. The
    protocol exists so tests can inject a stub without touching transformers.
    """

    def summarize(self, text: str, max_length: int, min_length: int) -> str: ...


class _HfSeq2SeqBackend:
    """Seq2seq summarization driven by transformers + torch.

    Built in `_default_backend_factory` so the heavy imports happen at
    load() time, never at module import. Mutable state lives entirely
    on the instance; no module-level globals.
    """

    def __init__(self, model: Any, tokenizer: Any, max_input_length: int) -> None:
        self._model = model
        self._tokenizer = tokenizer
        self._max_input_length = max_input_length

    def summarize(self, text: str, max_length: int, min_length: int) -> str:
        import torch

        inputs = self._tokenizer(
            text,
            return_tensors="pt",
            max_length=self._max_input_length,
            truncation=True,
        )
        with torch.inference_mode():
            outputs = self._model.generate(
                **inputs,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
            )
        return self._tokenizer.decode(outputs[0], skip_special_tokens=True).strip()


def _default_backend_factory(
    model_name: str, revision: str, max_input_length: int
) -> SummarizationBackend:
    # Imported lazily so tests can inject a backend without paying the
    # transformers import cost. The transformers module ships as a
    # _LazyModule whose internals swap sys.modules entries on attribute
    # set, which breaks naive monkeypatching — route mocking through
    # this seam instead.
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name, revision=revision)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, revision=revision)
    return _HfSeq2SeqBackend(model, tokenizer, max_input_length)


BackendFactory = Callable[[str, str, int], SummarizationBackend]


class ModelHolder:
    def __init__(
        self,
        model: str,
        revision: str,
        max_input_length: int = 1024,
        backend_factory: BackendFactory = _default_backend_factory,
    ) -> None:
        self._model = model
        self._revision = revision
        self._max_input_length = max_input_length
        self._backend_factory = backend_factory
        self._backend: SummarizationBackend | None = None
        self._lock = threading.Lock()
        self._loaded = False
        self._ready = False

    @property
    def model(self) -> str:
        return self._model

    @property
    def revision(self) -> str:
        return self._revision

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def is_ready(self) -> bool:
        return self._ready

    def load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            logger.info("Loading model %s @ %s", self._model, self._revision)
            self._backend = self._backend_factory(
                self._model, self._revision, self._max_input_length
            )
            self._loaded = True
            logger.info("Model loaded")

    def mark_ready(self) -> None:
        self._ready = True

    def summarize(self, text: str, max_length: int, min_length: int) -> str:
        if self._backend is None:
            raise RuntimeError("Model not loaded — call load() first")
        return self._backend.summarize(text, max_length, min_length)

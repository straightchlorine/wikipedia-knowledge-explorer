import threading

import torch
from sentence_transformers import SentenceTransformer
from transformers import pipeline


class ModelCache:
    """Lazy-loading singleton cache for ML models."""

    _instance = None
    _lock = threading.Lock()

    _embedding_model = None
    _summarization_pipeline = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def device(self) -> str:
        return "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def embedding_model(self) -> SentenceTransformer:
        if self._embedding_model is None:
            with self._lock:
                if self._embedding_model is None:
                    self._embedding_model = SentenceTransformer(
                        "all-MiniLM-L6-v2", device=self.device
                    )
        return self._embedding_model

    @property
    def summarization_pipeline(self):
        if self._summarization_pipeline is None:
            with self._lock:
                if self._summarization_pipeline is None:
                    self._summarization_pipeline = pipeline(
                        "summarization",
                        model="facebook/bart-large-cnn",
                        tokenizer="facebook/bart-large-cnn",
                    )
        return self._summarization_pipeline

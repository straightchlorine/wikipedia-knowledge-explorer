from typing import Any

import numpy as np

from wiki.processors.text.vectorizers.vectorizer import VectorizerBase
from wiki.services.model_cache import ModelCache


class EmbeddingVectorizer(VectorizerBase):
    """Sentence transformer based vectorization."""

    def __init__(self):
        cache = ModelCache()
        self.model = cache.embedding_model

    def vectorize(self, texts: list[str]) -> tuple[np.ndarray, Any]:
        """Convert texts to semantic embeddings."""
        embeddings = self.model.encode(texts)
        return embeddings, self.model

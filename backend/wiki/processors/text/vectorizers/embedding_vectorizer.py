from typing import Any


import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from wiki.processors.text.vectorizers.vectorizer import VectorizerBase


class EmbeddingVectorizer(VectorizerBase):
    """Sentence transformer based vectorization."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a sentence transformer model.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)

    def vectorize(self, texts: list[str]) -> tuple[np.ndarray, Any]:
        """Convert texts to semantic embeddings."""

        embeddings = self.model.encode(texts)
        return embeddings, self.model

from abc import ABC, abstractmethod

import numpy as np


class PostProcessor(ABC):
    """Abstract base class for post-processing cluster results."""

    @abstractmethod
    def process(
        self,
        labels: list[int],
        texts: list[str],
        vectors: np.ndarray,
        **kwargs,
    ) -> list[int]:
        """
        Post-process clustering results.

        Args:
            labels: Initial cluster labels
            texts: Original text documents
            vectors: Document vectors used for clustering
            **kwargs: Additional arguments

        Returns:
            Updated cluster labels
        """
        pass

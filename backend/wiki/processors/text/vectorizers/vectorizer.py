from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class VectorizerBase(ABC):
    """Abstract base class for text vectorization."""

    @abstractmethod
    def vectorize(self, texts: list[str]) -> tuple[np.ndarray, Any]:
        """
        Convert texts to vectors.

        Returns:
            Tuple containing the feature matrix and the fitted vectorizer
        """
        pass

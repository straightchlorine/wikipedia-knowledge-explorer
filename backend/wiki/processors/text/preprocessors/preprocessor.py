from abc import ABC, abstractmethod


class TextPreprocessor(ABC):
    """Abstract base class for text preprocessing."""

    @abstractmethod
    def preprocess(self, texts: list[str]) -> list[str]:
        """Preprocess a list of texts."""
        pass

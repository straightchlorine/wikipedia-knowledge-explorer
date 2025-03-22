from abc import ABC, abstractmethod


class TextSummarizer(ABC):
    """Abstract base class for text preprocessing."""

    @abstractmethod
    def summarize(self, texts: str) -> str:
        """Summarize a list of texts."""
        pass

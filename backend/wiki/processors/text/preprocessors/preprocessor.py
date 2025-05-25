from abc import ABC, abstractmethod

from wiki.processors.text.summarizers.summarizer import TextSummarizer


class TextPreprocessor(ABC):
    """Abstract base class for text preprocessing."""

    summarizer: TextSummarizer | None

    @abstractmethod
    def preprocess(self, texts: list[str]) -> list[str]:
        """Preprocess a list of texts."""
        pass

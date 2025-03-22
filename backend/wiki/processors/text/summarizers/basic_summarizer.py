from wiki.processors.text.summarizers.summarizer import TextSummarizer


class BasicSummarizer(TextSummarizer):
    """Basic text summarizer"""

    def summarize(self, texts: str) -> str:
        """Basic summarization of a text."""
        # extend the logic
        return texts[:100]

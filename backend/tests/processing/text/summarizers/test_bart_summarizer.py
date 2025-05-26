import pytest
from wiki.processors.text.summarizers.bart_summarizer import BartSummarizer


class TestBasicSummarizerBART:
    @pytest.fixture(scope="class")
    def summarizer(self):
        return BartSummarizer()

    def test_summarize_short_article(self, summarizer):
        """Test if BART summarizer returns a string summary shorter than input."""
        text = (
            "Natural language processing is a subfield of AI. "
            "It focuses on the interaction between computers and humans. "
            "Tasks include translation, sentiment analysis, and text generation."
        )
        summary = summarizer.summarize(text)
        assert isinstance(summary, str)
        assert len(summary.strip()) > 0
        assert len(summary.split()) < len(text.split())

    def test_summarize_truncates_long_text(self, summarizer):
        """Test that long text is summarized into something shorter."""
        long_text = " ".join(["This is a long sentence."] * 200)
        summary = summarizer.summarize(long_text)
        assert isinstance(summary, str)
        assert len(summary.strip()) > 0
        assert len(summary.split()) < len(long_text.split())

    def test_summarize_empty_input(self, summarizer):
        """Test how model handles empty string."""
        summary = summarizer.summarize("")
        assert isinstance(summary, str)
        assert summary.strip() == ""

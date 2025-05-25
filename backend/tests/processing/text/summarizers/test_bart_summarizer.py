import pytest
from wiki.processors.text.summarizers.bart_summarizer import BartSummarizer


class TestBasicSummarizerBART:
    @pytest.fixture(scope="class")
    def summarizer(self):
        return BartSummarizer()

    def test_summarize_short_article(self, summarizer):
        """Test if BART summarizer returns a string summary."""
        text = (
            "Natural language processing is a subfield of AI. "
            "It focuses on the interaction between computers and humans. "
            "Tasks include translation, sentiment analysis, and text generation."
        )
        summary = summarizer.summarize(text)
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert len(summary) <= 100  # due to max_length

    def test_summarize_truncates_long_text(self, summarizer):
        """Test that long text is truncated and summarized."""
        long_text = " ".join(["This is a long sentence."] * 200)  # >1024 chars
        summary = summarizer.summarize(long_text)
        assert isinstance(summary, str)
        assert len(summary) <= 100

    def test_summarize_empty_input(self, summarizer):
        """Test how model handles empty string."""
        with pytest.raises(Exception):  # or catch specific one if known
            summarizer.summarize("")

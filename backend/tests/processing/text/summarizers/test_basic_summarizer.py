from wiki.processors.text.summarizers.basic_summarizer import BasicSummarizer


class TestBasicSummarizer:
    def test_summarize_truncates_text(self):
        """Test that summarize truncates text to 100 characters."""
        summarizer = BasicSummarizer()
        long_text = "a" * 200
        result = summarizer.summarize(long_text)
        assert len(result) == 100

    def test_summarize_short_text(self):
        """Test summarize with text shorter than 100 characters."""
        summarizer = BasicSummarizer()
        short_text = "This is a short text."
        result = summarizer.summarize(short_text)
        assert result == short_text

    def test_summarize_empty_text(self):
        """Test summarize with empty text."""
        summarizer = BasicSummarizer()
        empty_text = ""
        result = summarizer.summarize(empty_text)
        assert result == empty_text

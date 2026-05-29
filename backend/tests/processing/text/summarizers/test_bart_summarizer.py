from unittest.mock import MagicMock, patch

import pytest

from wiki.processors.text.summarizers.bart_summarizer import BartSummarizer


class TestBartSummarizer:
    @patch("wiki.processors.text.summarizers.bart_summarizer.ModelCache")
    def test_summarize_returns_string(self, mock_cache_cls):
        """Test that summarize returns a string."""
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{"summary_text": "A summary of the text."}]
        mock_cache = MagicMock()
        mock_cache.summarization_pipeline = mock_pipeline
        mock_cache_cls.return_value = mock_cache

        summarizer = BartSummarizer()
        result = summarizer.summarize("Some input text to summarize.")

        assert isinstance(result, str)
        assert result == "A summary of the text."

    @patch("wiki.processors.text.summarizers.bart_summarizer.ModelCache")
    def test_summarize_empty_input(self, mock_cache_cls):
        """Test that empty input returns empty string."""
        mock_cache = MagicMock()
        mock_cache_cls.return_value = mock_cache

        summarizer = BartSummarizer()
        result = summarizer.summarize("")

        assert result == ""

    @patch("wiki.processors.text.summarizers.bart_summarizer.ModelCache")
    def test_summarize_truncates_long_input(self, mock_cache_cls):
        """Test that long input is truncated to 1024 chars before summarizing."""
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{"summary_text": "Summary."}]
        mock_cache = MagicMock()
        mock_cache.summarization_pipeline = mock_pipeline
        mock_cache_cls.return_value = mock_cache

        summarizer = BartSummarizer()
        long_text = "a" * 2000
        summarizer.summarize(long_text)

        # The pipeline should receive at most 1024 chars
        call_args = mock_pipeline.call_args
        assert len(call_args[0][0]) <= 1024

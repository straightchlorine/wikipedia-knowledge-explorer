import pytest
from wiki.processors.text.summarizers.tf_idf_summarizer import TFIDFSummarizer


class TestBasicSummarizerTFIDF:
    def test_summarize_returns_sentences(self):
        summarizer = TFIDFSummarizer()
        text = (
            "Natural language processing (NLP) is a subfield of linguistics, computer science, "
            "and artificial intelligence concerned with the interactions between computers and human language. "
            "It enables computers to understand and generate human language."
        )
        summary = summarizer.summarize(text, ratio=0.3)
        assert isinstance(summary, str)
        assert len(summary.strip()) > 0
        assert len(summary.split(".")) < len(text.split("."))

    def test_summarize_empty_input(self):
        """Ensure empty input returns empty string."""
        summarizer = TFIDFSummarizer()
        result = summarizer.summarize("")
        assert result == ""

    def test_summarize_single_sentence(self):
        summarizer = TFIDFSummarizer()
        text = "This is a single sentence."
        result = summarizer.summarize(text, ratio=1.0)
        assert isinstance(result, str)
        assert result.strip() == text

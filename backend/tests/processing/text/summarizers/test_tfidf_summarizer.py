import pytest
from wiki.processors.text.summarizers.tf_idf_summarizer import BasicSummarizer


class TestBasicSummarizerTFIDF:
    def test_summarize_returns_sentences(self):
        """Test that summarizer returns summary with at least one sentence."""
        summarizer = BasicSummarizer()
        text = (
            "Natural language processing (NLP) is a subfield of linguistics, computer science, "
            "and artificial intelligence concerned with the interactions between computers and human language."
            " NLP is used to apply algorithms to identify and extract the natural language rules "
            "such that the unstructured language data is converted into a form that computers can understand."
        )
        result = summarizer.summarize(text)
        assert isinstance(result, str)
        assert len(result.strip()) > 0
        assert len(result.split()) < len(text.split())

    def test_summarize_empty_input(self):
        """Ensure empty input raises an informative exception."""
        summarizer = BasicSummarizer()
        with pytest.raises(ValueError, match="empty vocabulary"):
            summarizer.summarize("")

    def test_summarize_single_sentence(self):
        """Ensure summarizer returns the original sentence if it's the only one."""
        summarizer = BasicSummarizer()
        text = "This is a single sentence."
        result = summarizer.summarize(text)
        assert isinstance(result, str)
        assert result.strip() == text

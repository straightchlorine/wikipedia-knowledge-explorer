from wiki.processors.text.summarizers.tf_idf_summarizer import BasicSummarizer


class TestBasicSummarizerTFIDF:
    def test_summarize_returns_sentences(self):
        """Ensure that the summarizer returns some of the original sentences."""
        summarizer = BasicSummarizer()
        text = (
            "Artificial intelligence is evolving rapidly. "
            "It is transforming industries worldwide. "
            "However, challenges like bias remain. "
            "Researchers continue to explore its potential."
        )
        result = summarizer.summarize(text)
        assert result != ""
        assert any(sentence in result for sentence in text.split(". "))

    def test_summarize_empty_input(self):
        """Ensure empty input returns empty output."""
        summarizer = BasicSummarizer()
        result = summarizer.summarize("")
        assert result == ""

    def test_summarize_single_sentence(self):
        """Ensure single sentence is returned as-is."""
        summarizer = BasicSummarizer()
        sentence = "This is the only sentence."
        result = summarizer.summarize(sentence)
        assert result == sentence

from wiki.processors.text.preprocessors.basic_preprocessor import BasicPreprocessor
from wiki.processors.text.summarizers.basic_summarizer import BasicSummarizer


class TestBasicPreprocessor:
    def test_preprocess_removes_html_tags(self):
        """Test that HTML tags are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["<p>This is a paragraph</p>"]
        result = preprocessor.preprocess(text)
        assert "<p>" not in result[0]
        assert "</p>" not in result[0]

    def test_preprocess_removes_citations(self):
        """Test that citations are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["This is a text with a citation[1]."]
        result = preprocessor.preprocess(text)
        assert "[1]" not in result[0]

    def test_preprocess_removes_special_characters(self):
        """Test that special characters are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["This text has special characters: !@#$%^&*()"]
        result = preprocessor.preprocess(text)
        assert "!@#$%^&*()" not in result[0]

    def test_preprocess_removes_digits(self):
        """Test that digits are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["This text has digits: 12345"]
        result = preprocessor.preprocess(text)
        assert "12345" not in result[0]

    def test_preprocess_converts_to_lowercase(self):
        """Test that text is converted to lowercase."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["This Text Has UPPERCASE Letters"]
        result = preprocessor.preprocess(text)
        assert result[0] == result[0].lower()

    def test_preprocess_removes_stopwords(self):
        """Test that stopwords are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["This is a sentence with stopwords."]
        result = preprocessor.preprocess(text)

        # stopwords like 'is', 'a', 'with' should be removed
        for stopword in ["is", "a", "with"]:
            assert stopword not in result[0].split()

    def test_preprocess_applies_lemmatization(self):
        """Test that lemmatization is applied during preprocessing."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        text = ["The cats are running and jumping"]
        result = preprocessor.preprocess(text)

        # 'cats' should be lemmatized to 'cat', 'running' to 'run', etc.
        assert "cat" in result[0]
        assert "run" in result[0]
        assert "jump" in result[0]

    def test_preprocess_multiple_texts(self):
        """Test preprocessing multiple texts."""
        preprocessor = BasicPreprocessor()
        preprocessor.summarizer = None
        texts = ["Text one!", "Text two!"]
        results = preprocessor.preprocess(texts)
        assert len(results) == 2
        assert all(isinstance(r, str) for r in results)

    def test_with_summarizer_enabled(self):
        """Test preprocessing with summarizer enabled."""
        preprocessor = BasicPreprocessor()

        preprocessor.summarizer = BasicSummarizer()
        text = ["a" * 200]
        result = preprocessor.preprocess(text)

        assert len(result[0]) <= 100

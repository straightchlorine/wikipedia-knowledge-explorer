from wiki.processors.text.preprocessors.basic_preprocessor import BasicPreprocessor


class TestBasicPreprocessor:
    def test_preprocess_removes_html_tags(self):
        """Test that HTML tags are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        text = ["<p>This is a paragraph</p>"]
        result = preprocessor.preprocess(text)
        assert "<p>" not in result[0]
        assert "</p>" not in result[0]
        assert "This is a paragraph" in result[0]

    def test_preprocess_removes_citations(self):
        """Test that citations are removed during preprocessing."""
        preprocessor = BasicPreprocessor()
        text = ["This is a text with a citation[1]."]
        result = preprocessor.preprocess(text)
        assert "[1]" not in result[0]

    def test_preprocess_normalizes_whitespace(self):
        """Test that excess whitespace is normalized."""
        preprocessor = BasicPreprocessor()
        text = ["This   has    extra   whitespace"]
        result = preprocessor.preprocess(text)
        assert result[0] == "This has extra whitespace"

    def test_preprocess_preserves_natural_text(self):
        """Test that natural text is preserved for SentenceTransformer."""
        preprocessor = BasicPreprocessor()
        text = ["The cats are running and jumping quickly"]
        result = preprocessor.preprocess(text)
        # Natural text should be preserved (no lemmatization/stopword removal)
        assert "cats" in result[0]
        assert "are" in result[0]
        assert "running" in result[0]
        assert "and" in result[0]

    def test_preprocess_multiple_texts(self):
        """Test preprocessing multiple texts."""
        preprocessor = BasicPreprocessor()
        texts = ["Text one!", "Text two!"]
        results = preprocessor.preprocess(texts)
        assert len(results) == 2
        assert all(isinstance(r, str) for r in results)

    def test_preprocess_strips_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        preprocessor = BasicPreprocessor()
        text = ["  hello world  "]
        result = preprocessor.preprocess(text)
        assert result[0] == "hello world"

    def test_preprocess_empty_list(self):
        """Test preprocessing empty list."""
        preprocessor = BasicPreprocessor()
        result = preprocessor.preprocess([])
        assert result == []

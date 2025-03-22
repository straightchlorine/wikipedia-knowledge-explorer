from unittest.mock import MagicMock, patch

import numpy as np

from wiki.processors.text.vectorizers.embedding_vectorizer import EmbeddingVectorizer


class TestEmbeddingVectorizer:
    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.SentenceTransformer")
    def test_initialization(self, mock_transformer):
        """Test that the vectorizer initializes with the default model."""
        EmbeddingVectorizer()
        mock_transformer.assert_called_once_with("all-MiniLM-L6-v2")

    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.SentenceTransformer")
    def test_initialization_custom_model(self, mock_transformer):
        """Test that the vectorizer initializes with a custom model."""
        EmbeddingVectorizer(model_name="custom-model")
        mock_transformer.assert_called_once_with("custom-model")

    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.SentenceTransformer")
    def test_vectorize_returns_embeddings_and_model(self, mock_transformer):
        """Test that vectorize returns both embeddings and the model."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_transformer.return_value = mock_model

        vectorizer = EmbeddingVectorizer()
        embeddings, model = vectorizer.vectorize(["Text 1", "Text 2"])

        assert model == mock_model
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 2)

    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.SentenceTransformer")
    def test_vectorize_calls_encode(self, mock_transformer):
        """Test that vectorize calls the model's encode method."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        mock_transformer.return_value = mock_model

        vectorizer = EmbeddingVectorizer()
        vectorizer.vectorize(["Text"])

        mock_model.encode.assert_called_once_with(["Text"])

from unittest.mock import MagicMock, patch

import numpy as np

from wiki.processors.text.vectorizers.embedding_vectorizer import EmbeddingVectorizer


class TestEmbeddingVectorizer:
    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.ModelCache")
    def test_vectorize_returns_embeddings_and_model(self, mock_cache_cls):
        """Test that vectorize returns both embeddings and the model."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_cache = MagicMock()
        mock_cache.embedding_model = mock_model
        mock_cache_cls.return_value = mock_cache

        vectorizer = EmbeddingVectorizer()
        embeddings, model = vectorizer.vectorize(["Text 1", "Text 2"])

        assert model == mock_model
        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (2, 2)

    @patch("wiki.processors.text.vectorizers.embedding_vectorizer.ModelCache")
    def test_vectorize_calls_encode(self, mock_cache_cls):
        """Test that vectorize calls the model's encode method."""
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1, 0.2]])
        mock_cache = MagicMock()
        mock_cache.embedding_model = mock_model
        mock_cache_cls.return_value = mock_cache

        vectorizer = EmbeddingVectorizer()
        vectorizer.vectorize(["Text"])

        mock_model.encode.assert_called_once_with(["Text"])

import numpy as np

from wiki.processors.clustering.postprocessing.similarity import SimilarityPostProcessor


class TestSimilarityPostProcessor:
    def test_initialization(self):
        """Test that SimilarityPostProcessor initializes with default threshold."""
        post_processor = SimilarityPostProcessor()
        assert post_processor.similarity_threshold == 0.4

    def test_initialization_custom_threshold(self):
        """Test that SimilarityPostProcessor initializes with custom threshold."""
        post_processor = SimilarityPostProcessor(similarity_threshold=0.5)
        assert post_processor.similarity_threshold == 0.5

    def test_process_few_samples(self):
        """Test processing with few samples (<=2)."""
        post_processor = SimilarityPostProcessor()
        labels = [0, 1]
        texts = ["Text 1", "Text 2"]
        vectors = np.array([[0.1, 0.2], [0.3, 0.4]])

        result = post_processor.process(labels, texts, vectors)

        # those should be original, unchanged labels
        assert result == labels

    def test_process_short_texts(self):
        """Test processing with short texts that might be similar."""
        post_processor = SimilarityPostProcessor(similarity_threshold=0.9)
        labels = [0, 1, 2]
        texts = [
            "Short text",
            "Another text",
            "Very long text with many words to make it different",
        ]

        # first two vectors are similar to each other
        vectors = np.array(
            [
                [0.9, 0.1],
                [0.9, 0.1],
                [0.1, 0.9],
            ]
        )

        result = post_processor.process(labels, texts, vectors)

        # first two in a single cluster, third in a separate one
        assert result[0] == result[1]
        assert result[2] != result[0]

    def test_process_long_texts(self):
        """Test processing with long texts that shouldn't be merged."""
        post_processor = SimilarityPostProcessor(similarity_threshold=0.9)
        labels = [0, 1, 2]

        texts = [
            "Long text " * 25,
            "Another long text " * 25,
            "Very different long text " * 25,
        ]

        vectors = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9]])
        result = post_processor.process(labels, texts, vectors)

        assert result == labels

    def test_process_zero_norm_vectors(self):
        """Test processing with zero-norm vectors (edge case)."""
        post_processor = SimilarityPostProcessor()
        labels = [0, 1, 2]
        texts = ["Short text", "Another text", "Third text"]

        vectors = np.array(
            [
                [0.0, 0.0],
                [0.9, 0.1],
                [0.1, 0.9],
            ]
        )

        result = post_processor.process(labels, texts, vectors)

        assert len(result) == 3
        assert all(isinstance(label, int) for label in result)

    def test_process_2d_vectors(self):
        """Test processing with 2D vectors (matrix per document)."""
        post_processor = SimilarityPostProcessor()
        labels = [0, 1, 2]
        texts = ["Short text", "Another text", "Third text"]

        vectors = np.array(
            [
                [[0.9, 0.1], [0.8, 0.2]],
                [[0.9, 0.1], [0.8, 0.2]],
                [[0.1, 0.9], [0.2, 0.8]],
            ]
        )

        result = post_processor.process(labels, texts, vectors)

        # 2D vectors should be accordingly handled
        assert len(result) == 3

        # and first two should be in the same cluster,
        # while the third one in different
        assert result[0] == result[1]
        assert result[2] != result[0]

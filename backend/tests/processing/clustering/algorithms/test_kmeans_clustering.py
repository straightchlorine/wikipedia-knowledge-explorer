from unittest.mock import MagicMock, patch

import numpy as np

from wiki.processors.clustering.algorithms.kmeans import KMeansClustering


class TestKMeansClustering:
    def test_find_clusters_empty_data(self):
        """Test clustering with empty data."""
        clustering = KMeansClustering()
        X = np.array([]).reshape(0, 2)
        result = clustering.find_clusters(X, max_clusters=5)

        assert result == []

    def test_find_clusters_single_sample(self):
        """Test clustering with a single sample."""
        clustering = KMeansClustering()
        X = np.array([[1.0, 2.0]])
        result = clustering.find_clusters(X, max_clusters=5)

        assert result == [0]

    def test_find_clusters_few_samples(self):
        """Test clustering with few samples (less than max_clusters)."""
        clustering = KMeansClustering()
        X = np.array([[1.0, 2.0], [5.0, 6.0]])
        result = clustering.find_clusters(X, max_clusters=5)

        assert len(result) == 2
        assert all(isinstance(label, int) for label in result)

    @patch("wiki.processors.clustering.algorithms.kmeans.KMeans")
    @patch("wiki.processors.clustering.algorithms.kmeans.silhouette_score")
    def test_find_clusters_uses_silhouette_for_all_k(self, mock_silhouette, mock_kmeans):
        """Test that find_clusters uses silhouette_score for all k >= 2."""
        mock_instances = []
        for k in range(2, 5):
            mock_instance = MagicMock()
            mock_instance.fit_predict.return_value = np.array(
                [i % k for i in range(8)]
            )
            mock_instance.inertia_ = 100 - k * 10
            mock_instances.append(mock_instance)

        final_mock = MagicMock()
        final_mock.fit_predict.return_value = np.array([0, 0, 0, 1, 1, 1, 0, 1])
        mock_instances.append(final_mock)

        mock_kmeans.side_effect = mock_instances

        # silhouette scores for k=2, k=3, k=4
        # with penalty 0.02*k: k=2: 0.8-0.04=0.76, k=3: 0.7-0.06=0.64, k=4: 0.6-0.08=0.52
        mock_silhouette.side_effect = [0.8, 0.7, 0.6]

        clustering = KMeansClustering()
        X = np.array([[i, i] for i in range(8)])
        result = clustering.find_clusters(X, max_clusters=4)

        # silhouette called for k=2, k=3, k=4
        assert mock_silhouette.call_count == 3

        assert result == final_mock.fit_predict.return_value.tolist()
        # best k should be 2 (highest penalized score)
        mock_kmeans.assert_called_with(n_clusters=2, random_state=42, n_init="auto")

    def test_find_clusters_no_hard_cap(self):
        """Test that there is no hard cap on cluster count."""
        clustering = KMeansClustering()
        # 20 samples should allow more than 4 clusters
        X = np.array([[i, i * 2] for i in range(20)])
        result = clustering.find_clusters(X, max_clusters=10)

        assert len(result) == 20
        assert all(isinstance(label, int) for label in result)

    def test_find_clusters_two_samples(self):
        """Test clustering with exactly two samples."""
        clustering = KMeansClustering()
        X = np.array([[0.0, 0.0], [10.0, 10.0]])
        result = clustering.find_clusters(X, max_clusters=5)

        assert len(result) == 2

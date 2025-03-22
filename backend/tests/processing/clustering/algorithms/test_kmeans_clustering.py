from unittest.mock import MagicMock, patch

import numpy as np

from wiki.processors.clustering.algorithms.kmeans import KMeansClustering


class TestKMeansClustering:
    def test_initialization(self):
        """Test that KMeansClustering initializes with default parameters."""
        clustering = KMeansClustering()
        assert clustering.random_state == 42
        assert clustering.n_init == "auto"

    def test_initialization_custom_params(self):
        """Test that KMeansClustering initializes with custom parameters."""
        clustering = KMeansClustering(random_state=100, n_init=5)
        assert clustering.random_state == 100
        assert clustering.n_init == 5

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
    def test_find_clusters_calls_kmeans(self, mock_kmeans):
        """Test that find_clusters calls KMeans with correct parameters."""
        # mock up KMeans instance
        mock_kmeans_instance = MagicMock()
        mock_kmeans_instance.fit_predict.return_value = np.array([0, 1, 0])
        mock_kmeans_instance.inertia_ = 10
        mock_kmeans.return_value = mock_kmeans_instance

        clustering = KMeansClustering()
        X = np.array([[1, 2], [3, 4], [1, 3]])
        clustering.find_clusters(X, max_clusters=3)

        # check if KMeans was called with correct parameters
        mock_kmeans.assert_called_with(n_clusters=2, random_state=42, n_init="auto")

    @patch("wiki.processors.clustering.algorithms.kmeans.KMeans")
    @patch("wiki.processors.clustering.algorithms.kmeans.silhouette_score")
    def test_find_clusters_uses_silhouette_score(self, mock_silhouette, mock_kmeans):
        """Test that find_clusters uses silhouette_score for k>=3."""
        # mock KMeans instances for different k values
        mock_instances = []
        for k in range(2, 5):
            mock_instance = MagicMock()
            mock_instance.fit_predict.return_value = np.array(
                [0] * (k // 2) + [1] * (k // 2)
            )

            # decrease inertia with increasing k
            mock_instance.inertia_ = 100 - k * 10
            mock_instances.append(mock_instance)

        # mock for the call with the best k
        final_mock = MagicMock()
        final_mock.fit_predict.return_value = np.array([0, 0, 0, 1, 1, 1])
        mock_instances.append(final_mock)

        mock_kmeans.side_effect = mock_instances

        # should be higher for k=3 i.e.
        # 0.7-0.3=0.4 vs 0.5-0.4=0.1
        mock_silhouette.side_effect = [0.7, 0.5]

        clustering = KMeansClustering()
        X = np.array([[i, i] for i in range(8)])
        result = clustering.find_clusters(X, max_clusters=4)

        assert mock_silhouette.call_count == 2

        assert result == final_mock.fit_predict.return_value.tolist()
        assert mock_kmeans.call_args_list[3][1]["n_clusters"] == 3

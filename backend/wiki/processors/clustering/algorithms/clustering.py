from abc import ABC, abstractmethod

import numpy as np


class ClusteringAlgorithm(ABC):
    """Abstract base class for clustering algorithms."""

    @abstractmethod
    def find_clusters(self, X: np.ndarray, max_clusters: int) -> list[int]:
        """
        Find clusters in the feature matrix.

        Args:
            X: Feature matrix to cluster
            max_clusters: Maximum number of clusters to consider

        Returns:
            List of cluster labels for each data point
        """
        pass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from wiki.processors.clustering.algorithms.clustering import ClusteringAlgorithm


class KMeansClustering(ClusteringAlgorithm):
    """K-Means clustering with automatic selection of cluster count."""

    def __init__(self, random_state: int = 42, n_init: str | int = "auto"):
        self.random_state = random_state
        self.n_init = n_init

    def find_clusters(self, X: np.ndarray, max_clusters: int) -> list[int]:
        """Find clusters using K-means with automatic selection of K."""

        # empty dataset
        if X.size == 0:
            return []

        # skip if there are no samples
        n_samples = X.shape[0]
        if n_samples <= 1:
            return [0] * n_samples

        # maximum possible number of clusters
        max_possible_clusters = min(max_clusters, n_samples - 1, 4)

        # skip if there are not enough samples for clustering
        if max_possible_clusters < 2:
            return [0] * n_samples

        # find the optimal number of clusters with 2 as the default
        best_k = 2
        best_score = -np.inf

        for k in range(2, max_possible_clusters + 1):
            kmeans = KMeans(
                n_clusters=k,
                random_state=self.random_state,
                n_init=self.n_init,
            )
            labels = kmeans.fit_predict(X)

            # skip if all samples end up in the same cluster
            if len(set(labels)) < 2:
                continue

            # silhouette score to evaluate clusters for k >= 3
            if k >= 3 and n_samples > 3:
                try:
                    sil_score = silhouette_score(X, labels)
                    # penalize higher k slightly to prevent overfitting
                    score = sil_score - (0.1 * k)
                except Exception:
                    score = -k
            else:
                # inertia for k < 3
                score = -kmeans.inertia_

            if score > best_score:
                best_score = score
                best_k = k

        # cluster with the best k
        final_kmeans = KMeans(
            n_clusters=best_k,
            random_state=self.random_state,
            n_init=self.n_init,
        )
        final_labels = final_kmeans.fit_predict(X)

        return final_labels.tolist()

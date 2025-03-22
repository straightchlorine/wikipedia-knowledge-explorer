import numpy as np

from wiki.processors.clustering.postprocessing.postprocessor import PostProcessor


class SimilarityPostProcessor(PostProcessor):
    """Post-processor that groups very similar articles together."""

    def __init__(self, similarity_threshold: float = 0.4):
        self.similarity_threshold = similarity_threshold

    def _calculate_similarity(self, vec_i, vec_j):
        """Calculate cosine similarity between two vectors or matrices."""

        # for 2D vectors (matrices), calculate similarity differently
        if vec_i.ndim > 1 and vec_j.ndim > 1:
            # average similarity across matching dimensions
            sims = []
            for row_i, row_j in zip(vec_i, vec_j):
                norm_i = np.linalg.norm(row_i)
                norm_j = np.linalg.norm(row_j)
                if norm_i > 0 and norm_j > 0:
                    sim = np.dot(row_i, row_j) / (norm_i * norm_j)
                    sims.append(sim)
            return np.mean(sims) if sims else 0
        else:
            # for 1D vectors, use standard cosine similarity
            vec_i_flat = vec_i.flatten() if vec_i.ndim > 1 else vec_i
            vec_j_flat = vec_j.flatten() if vec_j.ndim > 1 else vec_j

            # normalize to avoid division by zero
            norm_i = np.linalg.norm(vec_i_flat)
            norm_j = np.linalg.norm(vec_j_flat)

            if norm_i > 0 and norm_j > 0:
                return np.dot(vec_i_flat, vec_j_flat) / (norm_i * norm_j)
            else:
                return 0

    def process(
        self,
        labels: list[int],
        texts: list[str],
        vectors: np.ndarray,
        **kwargs,
    ) -> list[int]:
        """Group very similar articles into the same cluster."""
        final_labels = labels.copy()
        n_samples = len(texts)

        # process only if there is enough samples
        if n_samples <= 2:
            return final_labels

        # compare each document with short text to others
        for i in range(n_samples):
            # focus only on documents with short text (less than 50 words)
            if len(texts[i].split()) < 50:
                most_similar = None
                highest_sim = -1

                # find the most similar document
                for j in range(n_samples):
                    if i != j:
                        # calculate similarity between vectors
                        sim = self._calculate_similarity(vectors[i], vectors[j])
                        if sim > highest_sim:
                            highest_sim = sim
                            most_similar = j

                # similar enough, assign to same cluster
                if most_similar is not None and highest_sim > self.similarity_threshold:
                    final_labels[i] = final_labels[most_similar]

        return final_labels

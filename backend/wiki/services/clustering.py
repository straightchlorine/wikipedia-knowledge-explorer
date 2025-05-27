from wiki.processors.clustering.algorithms.kmeans import KMeansClustering
from wiki.processors.clustering.postprocessing.similarity import SimilarityPostProcessor
from wiki.processors.text.preprocessors.basic_preprocessor import BasicPreprocessor
from wiki.processors.text.vectorizers.embedding_vectorizer import EmbeddingVectorizer


def cluster_articles(
    texts: list[str], max_clusters: int = 3
) -> tuple[list[int], list[str]]:
    """
    Convert article text into vectors and apply clustering.

    Args:
        texts (list[str]): A list of article texts to be clustered.
        max_clusters (int): The maximum number of clusters to consider.
        Defaults to 5.

    Returns:
        list[int]: A list of cluster labels corresponding to each article.
    """

    # for none or one text, return [] or [0]
    if len(texts) <= 1:
        return [0] * len(texts), []

    # preprocess the contents
    processed_texts = BasicPreprocessor().preprocess(texts)

    # process text to embeddings
    embeddings, _ = EmbeddingVectorizer().vectorize(processed_texts)

    # find clusters based on embeddings
    labels = KMeansClustering().find_clusters(
        embeddings,
        max_clusters,
    )

    # return post-processed labels
    return SimilarityPostProcessor().process(
        labels,
        processed_texts,
        embeddings,
    )

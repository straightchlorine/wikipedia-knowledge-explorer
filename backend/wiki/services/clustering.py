"""Async clustering pipeline.

Summarization is now an I/O-bound call into the wke-summarizer service via
`SummarizerClient`. Clustering math (preprocess, vectorize, kmeans, similarity)
is CPU-bound and goes through `asyncio.to_thread` to keep the event loop free.
"""

from __future__ import annotations

import asyncio

from wiki.processors.clustering.algorithms.kmeans import KMeansClustering
from wiki.processors.clustering.postprocessing.similarity import SimilarityPostProcessor
from wiki.processors.text.preprocessors.basic_preprocessor import BasicPreprocessor
from wiki.processors.text.vectorizers.embedding_vectorizer import EmbeddingVectorizer
from wiki.services.summarizer_client import SummarizerClient


async def cluster_articles(
    texts: list[str],
    summarizer: SummarizerClient,
    max_clusters: int = 3,
) -> tuple[list[int], list[str]]:
    """Cluster article texts and produce per-article summaries.

    Returns (labels, summaries), one element per input text.
    """
    if len(texts) <= 1:
        summaries = await _summarize_texts(texts, summarizer) if texts else []
        return [0] * len(texts), summaries

    labels = await asyncio.to_thread(_cluster_only, texts, max_clusters)
    summaries = await _summarize_texts(texts, summarizer)
    return labels, summaries


def _cluster_only(texts: list[str], max_clusters: int) -> list[int]:
    """CPU-bound clustering pipeline; called inside asyncio.to_thread."""
    cleaned_texts = BasicPreprocessor().preprocess(texts)
    embeddings, _ = EmbeddingVectorizer().vectorize(cleaned_texts)
    labels = KMeansClustering().find_clusters(embeddings, max_clusters)
    labels, _ = SimilarityPostProcessor().process(labels, cleaned_texts, embeddings)
    return labels


async def _summarize_texts(texts: list[str], summarizer: SummarizerClient) -> list[str]:
    return list(await asyncio.gather(*(summarizer.summarize(t) for t in texts)))

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np

from wiki.services.clustering import cluster_articles


def _make_summarizer(returns):
    """Build an AsyncMock SummarizerClient whose summarize() yields `returns`."""
    summarizer = MagicMock()
    if isinstance(returns, list):
        summarizer.summarize = AsyncMock(side_effect=returns)
    else:
        summarizer.summarize = AsyncMock(return_value=returns)
    return summarizer


@patch("wiki.services.clustering.SimilarityPostProcessor")
@patch("wiki.services.clustering.EmbeddingVectorizer")
@patch("wiki.services.clustering.KMeansClustering")
@patch("wiki.services.clustering.BasicPreprocessor")
async def test_cluster_articles_returns_labels_and_summaries(
    mock_prep, mock_kmeans, mock_vec, mock_post
):
    mock_prep.return_value.preprocess.return_value = ["cleaned1", "cleaned2"]
    mock_vec.return_value.vectorize.return_value = (
        np.array([[0.1, 0.2], [0.3, 0.4]]),
        MagicMock(),
    )
    mock_kmeans.return_value.find_clusters.return_value = [0, 1]
    mock_post.return_value.process.return_value = ([0, 1], ["cleaned1", "cleaned2"])

    summarizer = _make_summarizer(["Sum1", "Sum2"])

    labels, summaries = await cluster_articles(["text1", "text2"], summarizer)

    assert labels == [0, 1]
    assert summaries == ["Sum1", "Sum2"]
    assert summarizer.summarize.await_count == 2


async def test_cluster_articles_empty_list():
    summarizer = _make_summarizer([])
    labels, summaries = await cluster_articles([], summarizer)
    assert labels == []
    assert summaries == []
    summarizer.summarize.assert_not_awaited()


async def test_cluster_articles_single_article():
    summarizer = _make_summarizer("Summary")
    labels, summaries = await cluster_articles(["some text"], summarizer)
    assert labels == [0]
    assert summaries == ["Summary"]
    summarizer.summarize.assert_awaited_once_with("some text")

import asyncio
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest

from wiki.main import wiki_exp

client = TestClient(wiki_exp)


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_success(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint when everything works correctly.
    """
    # mock return values of the functions
    mock_fetch_articles.return_value = [
        {"title": "Article 1", "pageid": 1},
        {"title": "Article 2", "pageid": 2},
    ]

    # each article returns a content string
    mock_fetch_content.side_effect = ["Content for article 1", "Content for article 2"]

    # clusters for the mock articles
    mock_cluster.return_value = [0, 1]

    response = client.get("/articles/clusters?query=test")
    data = response.json()
    articles = data["articles"]

    # check response's status and structure
    assert response.status_code == 200
    assert data["query"] == "test"
    assert len(articles) == 2

    # check if each has a cluster label
    for article in articles:
        assert "cluster" in article
        assert isinstance(article["cluster"], int)


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
async def test_cluster_endpoint_error(mock_fetch_articles):
    """
    Test the /articles/clusters endpoint when an error occurs.
    """
    # mock error during clustering process
    mock_fetch_articles.side_effect = Exception("Test error")

    response = client.get("/articles/clusters?query=test")

    # check if handled correctly
    assert response.status_code == 500
    assert "detail" in response.json()

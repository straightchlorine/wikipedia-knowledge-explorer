from unittest.mock import AsyncMock, Mock, patch

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
    mock_cluster.return_value = (
        [0, 1],
        ["Summary for article 1", "Summary for article2"],
    )

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


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_with_default_max_results(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint with default max_results value (5).
    """
    # mock article data
    mock_articles = [{"title": f"Article {i}", "pageid": i} for i in range(1, 6)]
    mock_fetch_articles.return_value = mock_articles

    # mock content for each article
    mock_fetch_content.side_effect = [f"Content for article {i}" for i in range(1, 6)]

    # mock cluster labels
    mock_cluster.return_value = (
        [i % 3 for i in range(5)],
        [f"Summary for article {i}" for i in range(5)],
    )

    # call endpoint without specifying max_results
    response = client.get("/articles/clusters?query=test")
    data = response.json()

    # verify correct number of articles returned
    assert response.status_code == 200
    assert len(data["articles"]) == 5

    # verify fetch_wikipedia_articles was called with default max_results
    mock_fetch_articles.assert_called_once_with("test", 5)


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_with_custom_max_results(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint with custom max_results value.
    """
    # Set custom max_results value
    custom_max = 10

    # mock article data for the custom max
    mock_articles = [
        {"title": f"Article {i}", "pageid": i} for i in range(1, custom_max + 1)
    ]
    mock_fetch_articles.return_value = mock_articles

    # mock content for each article
    mock_fetch_content.side_effect = [
        f"Content for article {i}" for i in range(1, custom_max + 1)
    ]

    # mock cluster labels
    mock_cluster.return_value = (
        [i % 4 for i in range(custom_max)],
        [f"Summary for article {i}" for i in range(custom_max)],
    )

    # call endpoint with custom max_results
    response = client.get(f"/articles/clusters?query=test&max_results={custom_max}")
    data = response.json()

    # verify correct number of articles returned
    assert response.status_code == 200
    assert len(data["articles"]) == custom_max

    # verify fetch_wikipedia_articles was called with custom max_results
    mock_fetch_articles.assert_called_once_with("test", custom_max)


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_with_zero_max_results(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint with max_results set to 0.
    """
    # mock empty article list
    mock_fetch_articles.return_value = []

    mock_cluster.return_value = ([], [])

    # call endpoint with max_results=0
    response = client.get("/articles/clusters?query=test&max_results=0")
    data = response.json()

    # verify empty articles list returned
    assert response.status_code == 200
    assert data["articles"] == []

    # verify fetch_wikipedia_articles was called with 0
    mock_fetch_articles.assert_called_once_with("test", 0)


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_with_negative_max_results(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint with negative max_results value.
    Negative values should be handled gracefully.
    """
    # call endpoint with negative max_results
    response = client.get("/articles/clusters?query=test&max_results=-5")

    assert response.status_code == 422
    assert "detail" in response.json()


@pytest.mark.asyncio
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles")
async def test_cluster_endpoint_fewer_results_than_requested(
    mock_cluster, mock_fetch_content, mock_fetch_articles
):
    """
    Test the /articles/clusters endpoint when fewer results are available than requested.
    """
    # maximum results to request
    max_results = 10

    # return fewer articles than requested
    available_articles = 3
    mock_articles = [
        {"title": f"Article {i}", "pageid": i} for i in range(1, available_articles + 1)
    ]
    mock_fetch_articles.return_value = mock_articles

    # mock content for each article
    mock_fetch_content.side_effect = [
        f"Content for article {i}" for i in range(1, available_articles + 1)
    ]

    # mock cluster labels
    mock_cluster.return_value = (
        [i % 2 for i in range(available_articles)],
        [f"Summary for article {i}" for i in range(available_articles)],
    )

    # call endpoint
    response = client.get(f"/articles/clusters?query=test&max_results={max_results}")
    data = response.json()

    # verify the correct number of articles returned (should be the available number)
    assert response.status_code == 200
    assert len(data["articles"]) == available_articles

    # verify fetch_wikipedia_articles was called with the requested max_results
    mock_fetch_articles.assert_called_once_with("test", max_results)

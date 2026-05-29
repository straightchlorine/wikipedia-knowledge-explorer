from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from wiki.main import wiki_exp
from wiki.routes.articles import get_summarizer


@pytest.fixture(autouse=True)
def stub_summarizer():
    """Override the SummarizerClient dependency with a benign mock for every test.

    The route patches `wiki.routes.articles.cluster_articles`, so the summarizer
    object is never actually invoked — it just needs to satisfy the Depends.
    """
    wiki_exp.dependency_overrides[get_summarizer] = lambda: MagicMock()
    yield
    wiki_exp.dependency_overrides.clear()


client = TestClient(wiki_exp, raise_server_exceptions=False)


@pytest.mark.parametrize("max_results,num_articles", [
    (None, 5),   # default
    (10, 10),    # custom
    (10, 3),     # fewer available than requested
])
@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
@patch("wiki.routes.articles.fetch_article_content", new_callable=AsyncMock)
@patch("wiki.routes.articles.cluster_articles", new_callable=AsyncMock)
def test_cluster_endpoint_success(
    mock_cluster, mock_fetch_content, mock_fetch_articles, max_results, num_articles
):
    """Test the /articles/clusters endpoint under various result-count scenarios."""
    mock_articles = [{"title": f"Article {i}", "pageid": i} for i in range(1, num_articles + 1)]
    mock_fetch_articles.return_value = mock_articles
    mock_fetch_content.side_effect = [f"Content for article {i}" for i in range(1, num_articles + 1)]
    mock_cluster.return_value = (
        [i % 3 for i in range(num_articles)],
        [f"Summary for article {i}" for i in range(num_articles)],
    )

    url = "/api/articles/clusters?query=test" + (f"&max_results={max_results}" if max_results else "")
    response = client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert data["query"] == "test"
    assert len(data["articles"]) == num_articles

    for article in data["articles"]:
        assert "cluster" in article
        assert isinstance(article["cluster"], int)

    expected_max = max_results if max_results else 5
    mock_fetch_articles.assert_called_once_with("test", expected_max)


@patch("wiki.routes.articles.fetch_wikipedia_articles", new_callable=AsyncMock)
def test_cluster_endpoint_error(mock_fetch_articles):
    """Test the /articles/clusters endpoint when an error occurs."""
    mock_fetch_articles.side_effect = Exception("Test error")

    response = client.get("/api/articles/clusters?query=test")

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


def test_cluster_endpoint_with_negative_max_results():
    """Test the /articles/clusters endpoint rejects negative max_results."""
    response = client.get("/api/articles/clusters?query=test&max_results=-5")
    assert response.status_code == 422
    assert "detail" in response.json()


def test_cluster_endpoint_max_results_too_large():
    """Test the /articles/clusters endpoint rejects max_results > 50."""
    response = client.get("/api/articles/clusters?query=test&max_results=100")
    assert response.status_code == 422
    assert "detail" in response.json()

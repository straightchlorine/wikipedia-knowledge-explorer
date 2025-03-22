from unittest.mock import patch

from fastapi.testclient import TestClient
from wiki.main import wiki_exp

client = TestClient(wiki_exp)


def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Wikipedia Knowledge Explorer API"}


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_success(mock_fetch):
    """Test the articles search endpoint with successful response."""
    # mock result
    mock_fetch.return_value = [
        {"title": "Article 1", "pageid": 12345},
        {"title": "Article 2", "pageid": 67890},
    ]

    response = client.get("/articles/?query=test")

    assert response.status_code == 200
    assert response.json() == {
        "query": "test",
        "articles": ["Article 1", "Article 2"],
    }


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_error(mock_fetch):
    """Test the articles search endpoint with error response."""

    # the side effect will be an exception
    mock_fetch.side_effect = Exception("API Error")

    response = client.get("/articles/?query=test")

    assert response.status_code == 500
    assert "detail" in response.json()

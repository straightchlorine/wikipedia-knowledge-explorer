from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from wiki.main import wiki_exp

client = TestClient(wiki_exp, raise_server_exceptions=False)


def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Wikipedia Knowledge Explorer API"}


@pytest.mark.parametrize("max_results,expected_call_arg", [
    (None, 5),   # default
    (15, 15),    # custom
])
@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_success(mock_fetch, max_results, expected_call_arg):
    mock_fetch.return_value = [{"title": "A1", "pageid": 1}, {"title": "A2", "pageid": 2}]
    url = "/api/articles/?query=test" + (f"&max_results={max_results}" if max_results else "")
    response = client.get(url)
    assert response.status_code == 200
    mock_fetch.assert_called_once_with("test", expected_call_arg)


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_error(mock_fetch):
    """Test the articles search endpoint with error response."""
    mock_fetch.side_effect = Exception("API Error")

    response = client.get("/api/articles/?query=test")

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


def test_search_articles_invalid_max_results():
    """Test the articles search endpoint with invalid max_results parameter."""
    response = client.get("/api/articles/?query=test&max_results=invalid")
    assert response.status_code == 422
    assert "detail" in response.json()


def test_search_articles_max_results_too_large():
    """Test the articles search endpoint rejects max_results > 50."""
    response = client.get("/api/articles/?query=test&max_results=100")
    assert response.status_code == 422
    assert "detail" in response.json()

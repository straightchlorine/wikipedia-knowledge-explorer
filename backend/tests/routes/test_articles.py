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


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_with_max_results(mock_fetch):
    """Test the articles search endpoint with custom max_results parameter."""
    # mock result
    mock_fetch.return_value = [
        {"title": "Article 1", "pageid": 12345},
        {"title": "Article 2", "pageid": 67890},
        {"title": "Article 3", "pageid": 54321},
    ]

    # testing with different max results
    response = client.get("/articles/?query=test&max_results=15")

    # check the response
    assert response.status_code == 200
    assert response.json() == {
        "query": "test",
        "articles": ["Article 1", "Article 2", "Article 3"],
    }

    # see if the fetch function was called with the correct parameters
    mock_fetch.assert_called_once_with("test", 15)


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_default_max_results(mock_fetch):
    """Test the articles search endpoint with default max_results."""

    # mock result
    mock_fetch.return_value = [
        {"title": "Article 1", "pageid": 12345},
        {"title": "Article 2", "pageid": 67890},
    ]

    # do not specify the max results (should be 5 - the default)
    response = client.get("/articles/?query=test")

    # verify response
    assert response.status_code == 200
    assert response.json() == {
        "query": "test",
        "articles": ["Article 1", "Article 2"],
    }

    # see if called correctly
    mock_fetch.assert_called_once_with("test", 5)


@patch("wiki.routes.articles.fetch_wikipedia_articles")
def test_search_articles_invalid_max_results(mock_fetch):
    """Test the articles search endpoint with invalid max_results parameter."""

    # invalid max_results
    response = client.get("/articles/?query=test&max_results=invalid")

    # check the response
    assert response.status_code == 422
    assert "detail" in response.json()

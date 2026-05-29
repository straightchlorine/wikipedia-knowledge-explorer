from unittest.mock import patch

from wiki.services.model_cache import ModelCache


def test_singleton_behavior():
    a = ModelCache()
    b = ModelCache()
    assert a is b


@patch("wiki.services.model_cache.SentenceTransformer")
@patch("wiki.services.model_cache.torch")
def test_lazy_loading(mock_torch, mock_st):
    mock_torch.cuda.is_available.return_value = False
    # Reset singleton state for a clean test
    ModelCache._embedding_model = None

    cache = ModelCache()
    # Model not loaded yet
    mock_st.assert_not_called()
    # Access triggers load
    _ = cache.embedding_model
    mock_st.assert_called_once()

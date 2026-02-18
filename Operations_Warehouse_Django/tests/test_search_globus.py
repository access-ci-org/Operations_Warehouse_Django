import pytest
from unittest.mock import patch
from resource_v4.views import SearchGlobus


@patch("resource_v4.views.globus_sdk.SearchClient")
def test_search_default_query(mock_search, factory):
    mock_client = mock_search.return_value
    mock_client.post_search.return_value = {"result": "ok"}

    request = factory.get("/search")
    view = SearchGlobus.as_view()
    response = view(request)

    assert response.status_code == 200


def test_invalid_param(factory):
    request = factory.get("/search", {"bad": "param"})

    view = SearchGlobus.as_view()
    response = view(request)

    assert response.status_code == 400

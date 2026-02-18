import pytest
from unittest.mock import patch
from resource_v4.views import populate_resource_v4_local_view


@patch("resource_v4.views.requests.get")
@patch("resource_v4.views.ResourceV4Local")
def test_populate_success(mock_model, mock_get, factory):
    mock_get.return_value.json.return_value = {
        "results": [{"ID": "1", "DetailURL": "x"}]
    }
    mock_get.return_value.raise_for_status.return_value = None

    request = factory.get("/populate")
    response = populate_resource_v4_local_view(request)

    assert response.status_code == 200

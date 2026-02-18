import pytest
from unittest.mock import patch
from resource_v4.views import compare_warehouse_view


@patch("resource_v4.views.GlobusProcess")
@patch("resource_v4.views.generate_payloads")
@patch("resource_v4.views.ApplicationHandle")
def test_compare_added(mock_handles, mock_payload, mock_globus, factory):
    mock_handles.objects.order_by.return_value.select_related.return_value = []

    mock_payload.return_value = {
        "added": [{"ID": "1", "EntityJSON": {}}],
        "removed": [],
        "updated": [],
    }

    request = factory.get("/compare")
    response = compare_warehouse_view(request)

    assert response.status_code == 200
    assert response.data[0]["added"] == 1

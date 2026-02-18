import pytest
from resource_v4.views import compare_dict_lists


def test_compare_added():
    old = []
    new = [{"LocalID": "1", "name": "test"}]

    result = compare_dict_lists(old, new)

    assert len(result["added"]) == 1


def test_compare_removed():
    old = [{"LocalID": "1"}]
    new = []

    result = compare_dict_lists(old, new)

    assert result["removed"] == ["1"]


def test_compare_updated_simple():
    old = [{"LocalID": "1", "name": "old"}]
    new = [{"LocalID": "1", "name": "new"}]

    result = compare_dict_lists(old, new)

    assert result["updated"][0]["changes"]["name"] == "new"


def test_nested_update():
    old = [{"LocalID": "1", "EntityJSON": {"a": 1}}]
    new = [{"LocalID": "1", "EntityJSON": {"a": 2}}]

    result = compare_dict_lists(old, new)

    assert result["updated"][0]["changes"]["EntityJSON"]["a"] == 2

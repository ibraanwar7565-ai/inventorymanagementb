"""Tests for the CLI helper functions (requests are mocked)."""

from unittest.mock import patch, MagicMock

from inventory_app import cli


def _mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    return mock


@patch("inventory_app.cli.requests.get")
def test_list_items(mock_get, capsys):
    mock_get.return_value = _mock_response(
        [{"id": 1, "name": "Widget", "quantity": 5, "price": 2.5, "brand": "Acme"}]
    )
    items = cli.list_items(api_url="http://test")
    assert items[0]["name"] == "Widget"
    assert "Widget" in capsys.readouterr().out


@patch("inventory_app.cli.requests.post")
def test_add_item(mock_post):
    mock_post.return_value = _mock_response({"id": 1, "name": "Widget"}, 201)
    item = cli.add_item("Widget", quantity=5, api_url="http://test")
    assert item["id"] == 1
    mock_post.assert_called_once()


@patch("inventory_app.cli.requests.patch")
def test_update_item(mock_patch):
    mock_patch.return_value = _mock_response({"id": 1, "quantity": 9})
    item = cli.update_item(1, {"quantity": 9}, api_url="http://test")
    assert item["quantity"] == 9


@patch("inventory_app.cli.requests.delete")
def test_delete_item(mock_delete):
    mock_delete.return_value = _mock_response({"message": "Item 1 deleted."})
    status = cli.delete_item(1, api_url="http://test")
    assert status == 200


@patch("inventory_app.cli.requests.post")
def test_import_from_openfoodfacts(mock_post):
    mock_post.return_value = _mock_response({"id": 1, "name": "Nutella"}, 201)
    data = cli.import_from_openfoodfacts("3017620422003", api_url="http://test")
    assert data["name"] == "Nutella"

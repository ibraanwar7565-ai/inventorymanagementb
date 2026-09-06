"""Tests for the OpenFoodFacts integration and the import route.

Network calls are mocked so the suite is fast and deterministic.
"""

from unittest.mock import patch, MagicMock

import pytest

from inventory_app import external_api, store
from inventory_app.app import create_app


PRODUCT_PAYLOAD = {
    "status": 1,
    "code": "3017620422003",
    "product": {
        "product_name": "Nutella",
        "code": "3017620422003",
        "brands": "Ferrero, Nutella",
        "generic_name": "Hazelnut spread",
    },
}


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield
    store.reset()


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def _mock_response(json_data, status_code=200):
    mock = MagicMock()
    mock.json.return_value = json_data
    mock.status_code = status_code
    mock.raise_for_status.return_value = None
    return mock


@patch("inventory_app.external_api.requests.get")
def test_fetch_by_barcode_found(mock_get):
    mock_get.return_value = _mock_response(PRODUCT_PAYLOAD)
    item = external_api.fetch_by_barcode("3017620422003")
    assert item["name"] == "Nutella"
    assert item["barcode"] == "3017620422003"
    assert item["brand"] == "Ferrero"


@patch("inventory_app.external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_get.return_value = _mock_response({"status": 0})
    assert external_api.fetch_by_barcode("0000") is None


@patch("inventory_app.external_api.requests.get")
def test_search_by_name(mock_get):
    mock_get.return_value = _mock_response(
        {"products": [PRODUCT_PAYLOAD["product"]]}
    )
    results = external_api.search_by_name("nutella")
    assert len(results) == 1
    assert results[0]["name"] == "Nutella"


@patch("inventory_app.external_api.requests.get")
def test_import_route_adds_to_inventory(mock_get, client):
    mock_get.return_value = _mock_response(PRODUCT_PAYLOAD)
    resp = client.post("/external/import", json={"barcode": "3017620422003", "quantity": 3})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Nutella"
    assert data["quantity"] == 3
    # the item is now in the inventory array
    assert len(store.all_items()) == 1


@patch("inventory_app.external_api.requests.get")
def test_import_route_not_found(mock_get, client):
    mock_get.return_value = _mock_response({"status": 0})
    resp = client.post("/external/import", json={"barcode": "0000"})
    assert resp.status_code == 404


def test_import_route_requires_barcode(client):
    resp = client.post("/external/import", json={})
    assert resp.status_code == 400

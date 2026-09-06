"""Tests for the CRUD REST API routes."""

import pytest

from inventory_app.app import create_app
from inventory_app import store


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


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_list_items_empty(client):
    resp = client.get("/items")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_item(client):
    resp = client.post("/items", json={"name": "Widget", "quantity": 5, "price": 2.5})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["id"] == 1
    assert data["name"] == "Widget"
    assert data["quantity"] == 5


def test_create_item_requires_name(client):
    resp = client.post("/items", json={"quantity": 5})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_read_item(client):
    client.post("/items", json={"name": "Widget"})
    resp = client.get("/items/1")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Widget"


def test_read_missing_item(client):
    resp = client.get("/items/999")
    assert resp.status_code == 404


def test_update_item(client):
    client.post("/items", json={"name": "Widget", "quantity": 1})
    resp = client.patch("/items/1", json={"quantity": 42})
    assert resp.status_code == 200
    assert resp.get_json()["quantity"] == 42
    # unchanged field is preserved
    assert resp.get_json()["name"] == "Widget"


def test_update_missing_item(client):
    resp = client.patch("/items/999", json={"quantity": 42})
    assert resp.status_code == 404


def test_delete_item(client):
    client.post("/items", json={"name": "Widget"})
    resp = client.delete("/items/1")
    assert resp.status_code == 200
    # confirm it is gone
    assert client.get("/items/1").status_code == 404


def test_delete_missing_item(client):
    resp = client.delete("/items/999")
    assert resp.status_code == 404


def test_search_items(client):
    client.post("/items", json={"name": "Coffee Mug"})
    client.post("/items", json={"name": "Laptop Backpack"})
    resp = client.get("/items/search?name=coffee")
    assert resp.status_code == 200
    results = resp.get_json()
    assert len(results) == 1
    assert results[0]["name"] == "Coffee Mug"

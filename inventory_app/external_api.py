"""Integration with the OpenFoodFacts external API.

These helpers fetch real product data so inventory records can be supplemented
with details (name, brand, barcode) pulled from OpenFoodFacts by barcode or by
a search term.

Docs: https://world.openfoodfacts.org/data
"""

import requests

BASE_URL = "https://world.openfoodfacts.org"
TIMEOUT = 10


def _product_to_item(product):
    """Convert an OpenFoodFacts product payload into our inventory item shape."""
    return {
        "name": product.get("product_name") or "Unknown product",
        "barcode": product.get("code") or product.get("_id"),
        "brand": (product.get("brands") or "").split(",")[0] or None,
        "description": product.get("generic_name") or product.get("product_name"),
        "quantity": 0,
        "price": None,
    }


def fetch_by_barcode(barcode):
    """Look up a single product by its barcode.

    Returns an inventory-shaped dict, or None if the product is not found.
    """
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != 1:
        return None

    return _product_to_item(payload["product"])


def search_by_name(name, page_size=5):
    """Search products by name.

    Returns a list of inventory-shaped dicts (possibly empty).
    """
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    response = requests.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    return [_product_to_item(product) for product in payload.get("products", [])]

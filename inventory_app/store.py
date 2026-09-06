"""In-memory data store for inventory items.

The inventory is kept in a simple Python list (the "database array"). Each item
is a dictionary. This module exposes small helper functions so the rest of the
application never touches the list directly, which keeps the storage logic in one
place and makes it easy to swap for a real database later.
"""

# The "database array" that holds every inventory item.
_inventory = []
_next_id = 1

# Fields an item may contain. `name` is required; the rest are optional.
ITEM_FIELDS = ("name", "barcode", "brand", "quantity", "price", "description")


def reset():
    """Empty the inventory. Used by the test-suite between tests."""
    global _inventory, _next_id
    _inventory = []
    _next_id = 1


def all_items():
    """Return the list of all items."""
    return _inventory


def find(item_id):
    """Return the item with the given id, or None if it does not exist."""
    return next((item for item in _inventory if item["id"] == item_id), None)


def find_by_barcode(barcode):
    """Return the first item matching a barcode, or None."""
    return next((item for item in _inventory if item.get("barcode") == barcode), None)


def search(name):
    """Return all items whose name contains `name` (case-insensitive)."""
    term = (name or "").lower()
    return [item for item in _inventory if term in (item.get("name") or "").lower()]


def create(data):
    """Create and store a new item from a dict of fields.

    Returns the created item (including its new id).
    """
    global _next_id
    item = {"id": _next_id}
    for field in ITEM_FIELDS:
        item[field] = data.get(field)
    # Default quantity to 0 when not supplied.
    if item["quantity"] is None:
        item["quantity"] = 0
    _inventory.append(item)
    _next_id += 1
    return item


def update(item_id, data):
    """Patch an existing item with the provided fields. Returns the item or None."""
    item = find(item_id)
    if item is None:
        return None
    for field in ITEM_FIELDS:
        if field in data:
            item[field] = data[field]
    return item


def delete(item_id):
    """Remove an item by id. Returns True if something was removed."""
    global _inventory
    item = find(item_id)
    if item is None:
        return False
    _inventory = [i for i in _inventory if i["id"] != item_id]
    return True

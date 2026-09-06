"""Command-line interface for the Inventory Management System.

The CLI talks to the running Flask REST API over HTTP using `requests`, so it
exercises the same endpoints an external client would. Start the API first
(`flask --app inventory_app.app run`), then run this CLI
(`python -m inventory_app.cli`).
"""

import sys
import requests

API_URL = "http://localhost:5000"


def list_items(api_url=API_URL):
    items = requests.get(f"{api_url}/items").json()
    if not items:
        print("Inventory is empty.")
        return items
    for item in items:
        print(
            f"[{item['id']}] {item['name']} "
            f"(qty: {item.get('quantity')}, price: {item.get('price')}, "
            f"brand: {item.get('brand')})"
        )
    return items


def add_item(name, quantity=0, price=None, brand=None, barcode=None, api_url=API_URL):
    payload = {
        "name": name,
        "quantity": quantity,
        "price": price,
        "brand": brand,
        "barcode": barcode,
    }
    item = requests.post(f"{api_url}/items", json=payload).json()
    print(f"Added item {item.get('id')}: {item.get('name')}")
    return item


def update_item(item_id, fields, api_url=API_URL):
    item = requests.patch(f"{api_url}/items/{item_id}", json=fields).json()
    print(f"Updated item {item_id}: {item}")
    return item


def delete_item(item_id, api_url=API_URL):
    resp = requests.delete(f"{api_url}/items/{item_id}")
    print(resp.json().get("message", resp.json()))
    return resp.status_code


def import_from_openfoodfacts(barcode, quantity=0, price=None, api_url=API_URL):
    """Fetch a product from OpenFoodFacts (via the API) and add it to inventory."""
    payload = {"barcode": barcode, "quantity": quantity, "price": price}
    resp = requests.post(f"{api_url}/external/import", json=payload)
    data = resp.json()
    if resp.status_code == 201:
        print(f"Imported '{data['name']}' as item {data['id']}.")
    else:
        print(f"Import failed: {data.get('error')}")
    return data


MENU = """
====== Inventory Management ======
1. List items
2. Add item
3. Update item
4. Delete item
5. Import item from OpenFoodFacts (by barcode)
6. Exit
"""


def main():  # pragma: no cover - interactive loop
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                list_items()
            elif choice == "2":
                name = input("Name: ")
                quantity = int(input("Quantity [0]: ") or 0)
                price = input("Price []: ") or None
                brand = input("Brand []: ") or None
                add_item(name, quantity, price, brand)
            elif choice == "3":
                item_id = int(input("Item id: "))
                field = input("Field to update: ")
                value = input("New value: ")
                update_item(item_id, {field: value})
            elif choice == "4":
                item_id = int(input("Item id: "))
                delete_item(item_id)
            elif choice == "5":
                barcode = input("Barcode: ")
                quantity = int(input("Quantity [0]: ") or 0)
                import_from_openfoodfacts(barcode, quantity)
            elif choice == "6":
                print("Goodbye!")
                break
            else:
                print("Invalid option, try again.")
        except requests.exceptions.ConnectionError:
            print("Could not reach the API. Is the Flask server running?")
        except Exception as exc:  # keep the CLI resilient
            print(f"Error: {exc}")


if __name__ == "__main__":
    sys.exit(main())

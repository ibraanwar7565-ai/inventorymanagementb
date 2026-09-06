# Inventory Management System

A Flask-based REST API for a small retail company's inventory, with an external
product-data integration (OpenFoodFacts) and a command-line client.

Built for the *Summative Lab: Python REST API with Flask – Inventory Management
System*.

## Features

- **REST API** with full CRUD for inventory items (create, read, update/patch, delete).
- **Helper routes**: health check and name search.
- **External API integration** with [OpenFoodFacts](https://world.openfoodfacts.org/):
  look up a product by barcode and add it straight into the inventory.
- **CLI** that talks to the API over HTTP (list, add, update, delete, import).
- **Unit tests** covering every feature (API, external integration, CLI).

## Project structure

```
.
├── inventory_app/
│   ├── __init__.py
│   ├── app.py            # Flask app factory + routes
│   ├── store.py          # in-memory "database array" + helpers
│   ├── external_api.py   # OpenFoodFacts integration
│   └── cli.py            # command-line client
├── tests/
│   ├── test_app.py           # CRUD route tests
│   ├── test_external_api.py  # external API + import tests (mocked)
│   └── test_cli.py           # CLI tests (mocked)
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the API

```bash
flask --app inventory_app.app run
# API available at http://localhost:5000
```

### Endpoints

| Method | Path                          | Description                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/health`                     | Service health check                     |
| GET    | `/items`                      | List all items                           |
| GET    | `/items/<id>`                 | Get one item                             |
| POST   | `/items`                      | Create an item (`name` required)         |
| PATCH  | `/items/<id>`                 | Update fields on an item                 |
| DELETE | `/items/<id>`                 | Delete an item                           |
| GET    | `/items/search?name=...`      | Search items by name                     |
| GET    | `/external/barcode/<barcode>` | Preview an OpenFoodFacts product         |
| POST   | `/external/import`            | Fetch by barcode and add to inventory    |

### Example requests

```bash
# Create an item
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Coffee Mug", "quantity": 12, "price": 9.99}'

# Update the quantity
curl -X PATCH http://localhost:5000/items/1 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 20}'

# Import a product from OpenFoodFacts by barcode
curl -X POST http://localhost:5000/external/import \
  -H "Content-Type: application/json" \
  -d '{"barcode": "3017620422003", "quantity": 5}'
```

## Running the CLI

Start the API first, then in another terminal:

```bash
python -m inventory_app.cli
```

You'll get a menu to list, add, update, delete, and import items from
OpenFoodFacts.

## Running the tests

```bash
pytest
```

All external network calls are mocked, so the suite runs offline and fast.

## Git workflow

Each feature was developed on its own branch and merged into `main` via a pull
request:

- `feature/crud-api` – REST CRUD routes and the in-memory store
- `feature/external-api` – OpenFoodFacts integration and import route
- `feature/cli` – command-line client

Merged feature branches were deleted after integration.

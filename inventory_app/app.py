"""Flask REST API for the Inventory Management System.

Routes
------
GET    /health                -> service health check (helper route)
GET    /items                 -> list all inventory items
GET    /items/<id>            -> read a single item
POST   /items                 -> create an item
PATCH  /items/<id>            -> update (patch) an item
DELETE /items/<id>            -> delete an item
GET    /items/search?name=... -> search items by name (helper route)
"""

from flask import Flask, jsonify, request

from . import store


def create_app():
    """Application factory so tests can create isolated app instances."""
    app = Flask(__name__)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "inventory-management"}), 200

    # ----- Read -----
    @app.route("/items", methods=["GET"])
    def list_items():
        return jsonify(store.all_items()), 200

    @app.route("/items/<int:item_id>", methods=["GET"])
    def get_item(item_id):
        item = store.find(item_id)
        if item is None:
            return jsonify({"error": f"Item {item_id} not found."}), 404
        return jsonify(item), 200

    # ----- Create -----
    @app.route("/items", methods=["POST"])
    def create_item():
        data = request.get_json(silent=True) or {}
        if not data.get("name"):
            return jsonify({"error": "The 'name' field is required."}), 400
        item = store.create(data)
        return jsonify(item), 201

    # ----- Update (patch) -----
    @app.route("/items/<int:item_id>", methods=["PATCH"])
    def update_item(item_id):
        data = request.get_json(silent=True) or {}
        item = store.update(item_id, data)
        if item is None:
            return jsonify({"error": f"Item {item_id} not found."}), 404
        return jsonify(item), 200

    # ----- Delete -----
    @app.route("/items/<int:item_id>", methods=["DELETE"])
    def delete_item(item_id):
        if not store.delete(item_id):
            return jsonify({"error": f"Item {item_id} not found."}), 404
        return jsonify({"message": f"Item {item_id} deleted."}), 200

    # ----- Helper: search -----
    @app.route("/items/search", methods=["GET"])
    def search_items():
        name = request.args.get("name", "")
        return jsonify(store.search(name)), 200

    return app


# Module-level app for `flask run` / `python -m inventory_app.app`.
app = create_app()


if __name__ == "__main__":
    app.run(port=5000, debug=True)

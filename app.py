from flask import Flask, jsonify, request
from external_api import find_product_by_barcode

app = Flask(__name__)


# Temporary inventory database
inventory = [
    {
        "id": 1,
        "name": "Coca Cola",
        "barcode": "5449000000996",
        "price": 100,
        "stock": 20
    },
    {
        "id": 2,
        "name": "Pepsi",
        "barcode": "5449000000439",
        "price": 100,
        "stock": 15
    }
]


# Home route
@app.route("/")
def home():
    return jsonify({
        "message": "Inventory Management API is running"
    })


# Get all inventory items
@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200


# Get one inventory item
@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            return jsonify(item), 200

    return jsonify({
        "error": "Item not found"
    }), 404


# Add a new inventory item
@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    required_fields = ["name", "barcode", "price", "stock"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({
            "error": "Price must be a non-negative number"
        }), 400

    if not isinstance(data["stock"], int) or data["stock"] < 0:
        return jsonify({
            "error": "Stock must be a non-negative integer"
        }), 400

    new_item = {
        "id": max([item["id"] for item in inventory], default=0) + 1,
        "name": data["name"],
        "barcode": data["barcode"],
        "price": data["price"],
        "stock": data["stock"]
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


# Update an inventory item
@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = None

    for existing_item in inventory:
        if existing_item["id"] == item_id:
            item = existing_item
            break

    if item is None:
        return jsonify({
            "error": "Item not found"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    if "price" in data:
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            return jsonify({
                "error": "Price must be a non-negative number"
            }), 400

    if "stock" in data:
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return jsonify({
                "error": "Stock must be a non-negative integer"
            }), 400

    if "name" in data:
        item["name"] = data["name"]

    if "barcode" in data:
        item["barcode"] = data["barcode"]

    if "price" in data:
        item["price"] = data["price"]

    if "stock" in data:
        item["stock"] = data["stock"]

    return jsonify(item), 200


# Delete an inventory item
@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    for item in inventory:
        if item["id"] == item_id:
            inventory.remove(item)

            return jsonify({
                "message": "Item deleted successfully"
            }), 200

    return jsonify({
        "error": "Item not found"
    }), 404


# Search OpenFoodFacts by barcode
@app.route("/external-products/<barcode>", methods=["GET"])
def get_external_product(barcode):
    product = find_product_by_barcode(barcode)

    if "error" in product:
        return jsonify(product), 404

    return jsonify(product), 200


# Add a product from OpenFoodFacts to inventory
@app.route("/inventory/from-api", methods=["POST"])
def add_from_external_api():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    # Check that barcode, price and stock were provided
    required_fields = ["barcode", "price", "stock"]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"Missing required field: {field}"
            }), 400

    # Validate price
    if not isinstance(data["price"], (int, float)) or data["price"] < 0:
        return jsonify({
            "error": "Price must be a non-negative number"
        }), 400

    # Validate stock
    if not isinstance(data["stock"], int) or data["stock"] < 0:
        return jsonify({
            "error": "Stock must be a non-negative integer"
        }), 400

    # Search OpenFoodFacts
    product = find_product_by_barcode(data["barcode"])

    # Stop if the external product could not be found
    if "error" in product:
        return jsonify(product), 404

    # Create the inventory item using the external product name
    new_item = {
        "id": max([item["id"] for item in inventory], default=0) + 1,
        "name": product["name"],
        "barcode": product["barcode"],
        "price": data["price"],
        "stock": data["stock"]
    }

    inventory.append(new_item)

    return jsonify(new_item), 201


# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
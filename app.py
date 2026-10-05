from flask import Flask, jsonify, request

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

    # Check if valid JSON was provided
    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    # Required fields
    required_fields = ["name", "barcode", "price", "stock"]

    # Check for missing fields
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

    # Create the new item
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
    # Find the item
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

    # Check if valid JSON was provided
    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    # Validate price if it is being updated
    if "price" in data:
        if not isinstance(data["price"], (int, float)) or data["price"] < 0:
            return jsonify({
                "error": "Price must be a non-negative number"
            }), 400

    # Validate stock if it is being updated
    if "stock" in data:
        if not isinstance(data["stock"], int) or data["stock"] < 0:
            return jsonify({
                "error": "Stock must be a non-negative integer"
            }), 400

    # Update only the fields provided
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


# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
import pytest
import app as app_module


@pytest.fixture(autouse=True)
def reset_inventory():
    """Reset inventory before every test."""
    app_module.inventory = [
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

    yield


@pytest.fixture
def client():
    """Create a Flask test client."""
    app_module.app.config["TESTING"] = True

    with app_module.app.test_client() as client:
        yield client


# -----------------------------
# HOME ROUTE TEST
# -----------------------------

def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory Management API is running"


# -----------------------------
# GET INVENTORY TESTS
# -----------------------------

def test_get_inventory(client):
    response = client.get("/inventory")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["name"] == "Coca Cola"


def test_get_single_inventory_item(client):
    response = client.get("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == 1
    assert data["name"] == "Coca Cola"


def test_get_missing_inventory_item(client):
    response = client.get("/inventory/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Item not found"


# -----------------------------
# POST INVENTORY TESTS
# -----------------------------

def test_create_inventory_item(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Fanta",
            "barcode": "123456789",
            "price": 80,
            "stock": 10
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["name"] == "Fanta"
    assert data["price"] == 80
    assert data["stock"] == 10


def test_create_inventory_missing_field(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Fanta",
            "price": 80,
            "stock": 10
        }
    )

    assert response.status_code == 400


def test_create_inventory_invalid_price(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Fanta",
            "barcode": "123456789",
            "price": -50,
            "stock": 10
        }
    )

    assert response.status_code == 400


def test_create_inventory_invalid_stock(client):
    response = client.post(
        "/inventory",
        json={
            "name": "Fanta",
            "barcode": "123456789",
            "price": 80,
            "stock": -10
        }
    )

    assert response.status_code == 400


# -----------------------------
# PATCH INVENTORY TESTS
# -----------------------------

def test_update_inventory_item(client):
    response = client.patch(
        "/inventory/1",
        json={
            "price": 150,
            "stock": 25
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["price"] == 150
    assert data["stock"] == 25


def test_update_missing_inventory_item(client):
    response = client.patch(
        "/inventory/999",
        json={
            "price": 150
        }
    )

    assert response.status_code == 404


def test_update_inventory_invalid_stock(client):
    response = client.patch(
        "/inventory/1",
        json={
            "stock": -5
        }
    )

    assert response.status_code == 400


# -----------------------------
# DELETE INVENTORY TESTS
# -----------------------------

def test_delete_inventory_item(client):
    response = client.delete("/inventory/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Item deleted successfully"


def test_delete_missing_inventory_item(client):
    response = client.delete("/inventory/999")

    assert response.status_code == 404


# -----------------------------
# EXTERNAL API TESTS
# -----------------------------

def test_external_product(client, monkeypatch):
    """Test successful OpenFoodFacts lookup."""

    def fake_find_product(barcode):
        return {
            "name": "Coca-Cola Original",
            "barcode": barcode,
            "brand": "Coca-Cola",
            "category": "Soft drinks"
        }

    monkeypatch.setattr(
        app_module,
        "find_product_by_barcode",
        fake_find_product
    )

    response = client.get(
        "/external-products/5449000000996"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["name"] == "Coca-Cola Original"
    assert data["barcode"] == "5449000000996"


def test_external_product_not_found(client, monkeypatch):
    """Test external API product not found."""

    def fake_find_product(barcode):
        return {
            "error": "Product not found"
        }

    monkeypatch.setattr(
        app_module,
        "find_product_by_barcode",
        fake_find_product
    )

    response = client.get(
        "/external-products/9999999999999"
    )

    assert response.status_code == 404


# -----------------------------
# ADD EXTERNAL PRODUCT TESTS
# -----------------------------

def test_add_external_product(client, monkeypatch):
    """Test adding a product from OpenFoodFacts."""

    def fake_find_product(barcode):
        return {
            "name": "Fanta Orange",
            "barcode": barcode,
            "brand": "Coca-Cola",
            "category": "Soft drinks"
        }

    monkeypatch.setattr(
        app_module,
        "find_product_by_barcode",
        fake_find_product
    )

    response = client.post(
        "/inventory/from-api",
        json={
            "barcode": "123456789",
            "price": 120,
            "stock": 20
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["name"] == "Fanta Orange"
    assert data["barcode"] == "123456789"
    assert data["price"] == 120
    assert data["stock"] == 20


def test_add_external_product_missing_barcode(client):
    response = client.post(
        "/inventory/from-api",
        json={
            "price": 120,
            "stock": 20
        }
    )

    assert response.status_code == 400


def test_add_external_product_invalid_price(client):
    response = client.post(
        "/inventory/from-api",
        json={
            "barcode": "123456789",
            "price": -10,
            "stock": 20
        }
    )

    assert response.status_code == 400


def test_add_external_product_external_failure(client, monkeypatch):
    """Test when OpenFoodFacts cannot find the product."""

    def fake_find_product(barcode):
        return {
            "error": "Product not found"
        }

    monkeypatch.setattr(
        app_module,
        "find_product_by_barcode",
        fake_find_product
    )

    response = client.post(
        "/inventory/from-api",
        json={
            "barcode": "9999999999999",
            "price": 100,
            "stock": 10
        }
    )

    assert response.status_code == 404

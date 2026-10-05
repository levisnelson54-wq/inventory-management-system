import requests


def find_product_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    headers = {
        "User-Agent": "InventoryManagementSystem/1.0 (Moringa Student Project)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "error": "External API request failed",
                "status_code": response.status_code
            }

        data = response.json()

        if data.get("status") != 1:
            return {
                "error": "Product not found"
            }

        product = data.get("product", {})

        return {
            "name": product.get("product_name", "Unknown"),
            "barcode": barcode,
            "brand": product.get("brands", "Unknown"),
            "category": product.get("categories", "Unknown")
        }

    except requests.RequestException as error:
        return {
            "error": f"Could not connect to OpenFoodFacts: {error}"
        }

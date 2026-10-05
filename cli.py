import requests


BASE_URL = "http://127.0.0.1:5000"


def view_inventory():
    """Display all inventory items."""
    try:
        response = requests.get(f"{BASE_URL}/inventory")

        if response.status_code == 200:
            items = response.json()

            print("\n--- Inventory ---")

            if not items:
                print("Inventory is empty.")
                return

            for item in items:
                print(
                    f"ID: {item['id']} | "
                    f"Name: {item['name']} | "
                    f"Barcode: {item['barcode']} | "
                    f"Price: {item['price']} | "
                    f"Stock: {item['stock']}"
                )
        else:
            print("Could not retrieve inventory.")

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def add_item():
    """Add a new inventory item."""
    print("\n--- Add Inventory Item ---")

    name = input("Enter product name: ")
    barcode = input("Enter barcode: ")

    try:
        price = float(input("Enter price: "))
        stock = int(input("Enter stock: "))
    except ValueError:
        print("Price must be a number and stock must be an integer.")
        return

    data = {
        "name": name,
        "barcode": barcode,
        "price": price,
        "stock": stock
    }

    try:
        response = requests.post(
            f"{BASE_URL}/inventory",
            json=data
        )

        if response.status_code == 201:
            print("\nItem added successfully!")
            print(response.json())
        else:
            print("\nError:")
            print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def update_item():
    """Update an inventory item's price or stock."""
    print("\n--- Update Inventory Item ---")

    try:
        item_id = int(input("Enter item ID: "))
    except ValueError:
        print("ID must be a number.")
        return

    print("Leave a field empty if you do not want to update it.")

    price_input = input("Enter new price: ")
    stock_input = input("Enter new stock: ")

    data = {}

    if price_input:
        try:
            data["price"] = float(price_input)
        except ValueError:
            print("Price must be a number.")
            return

    if stock_input:
        try:
            data["stock"] = int(stock_input)
        except ValueError:
            print("Stock must be an integer.")
            return

    if not data:
        print("No changes provided.")
        return

    try:
        response = requests.patch(
            f"{BASE_URL}/inventory/{item_id}",
            json=data
        )

        if response.status_code == 200:
            print("\nItem updated successfully!")
            print(response.json())
        else:
            print("\nError:")
            print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def delete_item():
    """Delete an inventory item."""
    print("\n--- Delete Inventory Item ---")

    try:
        item_id = int(input("Enter item ID: "))
    except ValueError:
        print("ID must be a number.")
        return

    try:
        response = requests.delete(
            f"{BASE_URL}/inventory/{item_id}"
        )

        if response.status_code == 200:
            print("\nItem deleted successfully!")
        else:
            print("\nError:")
            print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def find_external_product():
    """Find a product using OpenFoodFacts."""
    print("\n--- Find Product on OpenFoodFacts ---")

    barcode = input("Enter product barcode: ")

    try:
        response = requests.get(
            f"{BASE_URL}/external-products/{barcode}"
        )

        if response.status_code == 200:
            product = response.json()

            print("\n--- Product Found ---")
            print(f"Name: {product['name']}")
            print(f"Barcode: {product['barcode']}")
            print(f"Brand: {product['brand']}")
            print(f"Category: {product['category']}")

        else:
            print("\nProduct could not be found.")
            print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def add_external_product():
    """Find a product on OpenFoodFacts and add it to inventory."""
    print("\n--- Add Product From OpenFoodFacts ---")

    barcode = input("Enter product barcode: ")

    try:
        response = requests.get(
            f"{BASE_URL}/external-products/{barcode}"
        )

        if response.status_code != 200:
            print("\nProduct could not be found.")
            print(response.json())
            return

        product = response.json()

        print("\nProduct found:")
        print(f"Name: {product['name']}")
        print(f"Brand: {product['brand']}")
        print(f"Category: {product['category']}")

        try:
            price = float(input("Enter inventory price: "))
            stock = int(input("Enter inventory stock: "))
        except ValueError:
            print("Price must be a number and stock must be an integer.")
            return

        data = {
            "barcode": barcode,
            "price": price,
            "stock": stock
        }

        response = requests.post(
            f"{BASE_URL}/inventory/from-api",
            json=data
        )

        if response.status_code == 201:
            print("\nProduct added to inventory successfully!")
            print(response.json())
        else:
            print("\nCould not add product.")
            print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def main():
    """Display the CLI menu."""
    while True:
        print("\n==============================")
        print("   INVENTORY MANAGEMENT CLI")
        print("==============================")
        print("1. View inventory")
        print("2. Add inventory item")
        print("3. Update price/stock")
        print("4. Delete inventory item")
        print("5. Find product on OpenFoodFacts")
        print("6. Add product from OpenFoodFacts")
        print("7. Exit")

        choice = input("\nChoose an option: ")

        if choice == "1":
            view_inventory()

        elif choice == "2":
            add_item()

        elif choice == "3":
            update_item()

        elif choice == "4":
            delete_item()

        elif choice == "5":
            find_external_product()

        elif choice == "6":
            add_external_product()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1-7.")


if __name__ == "__main__":
    main()

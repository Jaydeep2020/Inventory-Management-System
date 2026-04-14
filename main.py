from product import Product
from inventory import Inventory
from manager import InventoryManager
from exception import InventoryException


def print_menu():
    print("\n===== Inventory Management System =====")
    print("1. Add Inventory")
    print("2. Add Product to Inventory")
    print("3. View Inventories")
    print("4. Fulfill Order")
    print("5. Transfer Stock")
    print("6. Exit")


def main():
    manager = InventoryManager()

    while True:
        print_menu()

        try:
            choice = int(input("Enter your choice: "))

            # 1. Add Inventory
            if choice == 1:
                # inv_id = int(input("Enter Inventory ID: "))
                name = input("Enter Inventory Name: ")

                inventory = Inventory(name)
                manager.add_inventory(inventory)

                print("✅ Inventory added successfully")

            # 2. Add Product
            elif choice == 2:
                inv_name = input("Enter Inventory Name: ")

                # product_id = int(input("Enter Product ID: "))
                product_name = input("Enter Product Name: ")
                quantity = int(input("Enter Quantity: "))
                price = float(input("Enter Price: "))

                inventory = manager.get_inventory(inv_name)

                product = Product(product_name, quantity, price)
                inventory.add_product(product)

                print("✅ Product added successfully")

            # 3. View Inventories
            elif choice == 3:
                inventories = manager.list_inventories()

                if not inventories:
                    print("⚠️ No inventories available")
                else:
                    for inv in inventories:
                        print(inv)

            # 4. Fulfill Order
            elif choice == 4:
                product_name = input("Enter Product Name: ")
                quantity = int(input("Enter Required Quantity: "))

                manager.fulfill_order(product_name, quantity)

            # 5. Transfer Stock
            elif choice == 5:
                product_name = input("Enter Product Name: ")
                quantity = int(input("Enter Quantity: "))
                source = input("Enter Source Inventory: ")
                target = input("Enter Target Inventory: ")

                manager.transfer_stock(product_name, quantity, source, target)

            # 6. Exit
            elif choice == 6:
                print("👋 Exiting system...")
                break

            else:
                print("❌ Invalid choice. Try again.")

        except ValueError:
            print("❌ Invalid input type. Please enter correct values.")

        except InventoryException as e:
            print(f"⚠️ Error: {e}")

        except Exception as e:
            print(f"🚨 Unexpected error: {e}")


if __name__ == "__main__":
    main()
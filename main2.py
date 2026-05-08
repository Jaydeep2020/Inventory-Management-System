#!/usr/bin/env python3
"""
CLI Inventory Management System
Replaces the Streamlit GUI with a text-based menu.
"""

from services.manager import InventoryManager
from services.inventory import Inventory
from services.product import GroceryProduct, ElectricalProduct
from exception import (
    InventoryNotFoundException,
    ProductNotFoundException,
    InsufficientStockException
)


def clear_screen():
    """Clear the terminal screen (optional, for cleaner output)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_success(message):
    print(f"✅ {message}")


def print_error(message):
    print(f"❌ {message}")


def print_info(message):
    print(f"ℹ️  {message}")


def display_menu():
    """Show the main menu and return the user's choice."""
    print_header("INVENTORY MANAGEMENT SYSTEM")
    print("1. Add Inventory")
    print("2. View Inventories")
    print("3. Delete Inventory")
    print("4. Add Product")
    print("5. View Products")
    print("6. Remove Product")
    print("7. Update Stock")
    print("8. Check Availability")
    print("9. Transfer Stock")
    print("10. Total Stock Report")
    print("0. Exit")
    print("-" * 60)
    choice = input("Enter your choice: ").strip()
    return choice


def add_inventory(manager):
    """Add a new inventory."""
    print_header("ADD INVENTORY")
    name = input("Inventory Name: ").strip()
    location = input("Location: ").strip()
    if not name or not location:
        print_error("Name and location are required.")
        return
    try:
        inv = Inventory(name, location)
        InventoryManager.add_inventory(inv)  # note: method is classmethod
        print_success(f"Inventory '{name}' added successfully.")
    except Exception as e:
        print_error(str(e))


def view_inventories():
    """Display all inventories."""
    print_header("ALL INVENTORIES")
    inventories = InventoryManager.list_inventories()
    if not inventories:
        print_info("No inventories found.")
    else:
        print(f"{'ID':<5} {'Name':<20} {'Location':<20}")
        print("-" * 45)
        for inv_id, name, location in inventories:
            print(f"{inv_id:<5} {name:<20} {location:<20}")
    input("\nPress Enter to continue...")


def delete_inventory():
    """Delete an inventory by name and location."""
    print_header("DELETE INVENTORY")
    name = input("Inventory Name: ").strip()
    location = input("Location: ").strip()
    if not name or not location:
        print_error("Name and location are required.")
        return
    try:
        InventoryManager.remove_inventory(name, location)
        print_success(f"Inventory '{name}' deleted successfully.")
    except InventoryNotFoundException as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def add_product():
    """Add a product to a specific inventory."""
    print_header("ADD PRODUCT")
    inv_name = input("Inventory Name: ").strip()
    inv_location = input("Inventory Location: ").strip()
    if not inv_name or not inv_location:
        print_error("Inventory name and location are required.")
        return

    # Get inventory id
    try:
        inv_data = InventoryManager.get_inventory(inv_name, inv_location)
        inv_id = inv_data[0]
    except InventoryNotFoundException as e:
        print_error(str(e))
        input("\nPress Enter to continue...")
        return

    product_type = input("Product Type (grocery/electrical): ").strip().lower()
    if product_type not in ("grocery", "electrical"):
        print_error("Invalid product type. Choose 'grocery' or 'electrical'.")
        return

    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return

    try:
        quantity = int(input("Quantity: ").strip())
        price = float(input("Price: ").strip())
    except ValueError:
        print_error("Quantity must be an integer and price a number.")
        return

    if product_type == "grocery":
        expiry = input("Expiry Date (YYYY-MM-DD): ").strip()
        if not expiry:
            print_error("Expiry date is required for grocery products.")
            return
        product = GroceryProduct(product_name, quantity, price, expiry)
    else:  # electrical
        try:
            warranty = int(input("Warranty (months): ").strip())
        except ValueError:
            print_error("Warranty must be an integer.")
            return
        product = ElectricalProduct(product_name, quantity, price, warranty)

    try:
        Inventory.add_product(product, inv_id)
        print_success(f"Product '{product_name}' added successfully.")
    except Exception as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def view_products():
    """List all products in a given inventory."""
    print_header("VIEW PRODUCTS")
    inv_name = input("Inventory Name: ").strip()
    inv_location = input("Inventory Location: ").strip()
    if not inv_name or not inv_location:
        print_error("Inventory name and location are required.")
        input("\nPress Enter to continue...")
        return

    try:
        inv_data = InventoryManager.get_inventory(inv_name, inv_location)
        inv_id = inv_data[0]
        products = Inventory.list_products(inv_id)
    except InventoryNotFoundException as e:
        print_error(str(e))
        input("\nPress Enter to continue...")
        return

    if not products:
        print_info("No products found in this inventory.")
    else:
        # Print as a table
        print("\n" + "-" * 100)
        print(f"{'Name':<20} {'Category':<12} {'Price':<8} {'Expiry':<12} {'Warranty':<10} {'Qty':<6}")
        print("-" * 100)
        for p in products:
            # p = (name, category, price, expiry, warranty, quantity)
            name, cat, price, expiry, warranty, qty = p
            expiry_str = expiry if expiry else "N/A"
            warranty_str = f"{warranty} mo" if warranty else "N/A"
            print(f"{name:<20} {cat:<12} {price:<8.2f} {expiry_str:<12} {warranty_str:<10} {qty:<6}")
        print("-" * 100)
    input("\nPress Enter to continue...")


def remove_product():
    """Remove a product from an inventory."""
    print_header("REMOVE PRODUCT")
    inv_name = input("Inventory Name: ").strip()
    inv_location = input("Inventory Location: ").strip()
    if not inv_name or not inv_location:
        print_error("Inventory name and location are required.")
        return
    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return

    try:
        inv_data = InventoryManager.get_inventory(inv_name, inv_location)
        Inventory.remove_product(product_name, inv_data)
        print_success(f"Product '{product_name}' removed successfully.")
    except ProductNotFoundException as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def update_stock():
    """Increase or decrease product stock."""
    print_header("UPDATE STOCK")
    inv_name = input("Inventory Name: ").strip()
    inv_location = input("Inventory Location: ").strip()
    if not inv_name or not inv_location:
        print_error("Inventory name and location are required.")
        return
    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return

    try:
        qty = int(input("Quantity change (positive to add, negative to remove): ").strip())
    except ValueError:
        print_error("Quantity must be an integer.")
        return

    try:
        inv_data = InventoryManager.get_inventory(inv_name, inv_location)
        Inventory.update_stock(product_name, qty, inv_data)
        print_success("Stock updated successfully.")
    except (ProductNotFoundException, InsufficientStockException) as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def check_availability():
    """Check if a requested quantity is available."""
    print_header("CHECK AVAILABILITY")
    inv_name = input("Inventory Name: ").strip()
    inv_location = input("Inventory Location: ").strip()
    if not inv_name or not inv_location:
        print_error("Inventory name and location are required.")
        return
    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return

    try:
        qty = int(input("Required Quantity: ").strip())
        if qty <= 0:
            print_error("Quantity must be positive.")
            return
    except ValueError:
        print_error("Quantity must be an integer.")
        return

    try:
        inv_data = InventoryManager.get_inventory(inv_name, inv_location)
        Inventory.check_availability(product_name, qty, inv_data[0])
        print_success("Product is available.")
    except (ProductNotFoundException, InsufficientStockException) as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def transfer_stock():
    """Transfer stock between two inventories."""
    print_header("TRANSFER STOCK")
    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return

    try:
        qty = int(input("Quantity to transfer: ").strip())
        if qty <= 0:
            print_error("Quantity must be positive.")
            return
    except ValueError:
        print_error("Quantity must be an integer.")
        return

    print("\n--- Source Inventory ---")
    src_name = input("Source Inventory Name: ").strip()
    src_loc = input("Source Location: ").strip()
    if not src_name or not src_loc:
        print_error("Source inventory details are required.")
        return

    print("\n--- Target Inventory ---")
    tgt_name = input("Target Inventory Name: ").strip()
    tgt_loc = input("Target Location: ").strip()
    if not tgt_name or not tgt_loc:
        print_error("Target inventory details are required.")
        return

    try:
        src_inv = InventoryManager.get_inventory(src_name, src_loc)
        tgt_inv = InventoryManager.get_inventory(tgt_name, tgt_loc)
        InventoryManager.transfer_stock(product_name, qty, src_inv[0], tgt_inv[0])
        print_success("Stock transferred successfully.")
    except (InventoryNotFoundException, ProductNotFoundException, InsufficientStockException) as e:
        print_error(str(e))
    input("\nPress Enter to continue...")


def total_stock_report():
    """Get total stock of a product across all inventories."""
    print_header("TOTAL STOCK REPORT")
    product_name = input("Product Name: ").strip()
    if not product_name:
        print_error("Product name is required.")
        return
    total = InventoryManager.get_total_stock(product_name)
    print_info(f"Total stock for '{product_name}' = {total}")
    input("\nPress Enter to continue...")


def main():
    """Main CLI loop."""
    # Ensure manager is created (global-like, but we don't need session state)
    # The InventoryManager class itself holds static data; we just call its methods.
    # We can also create an instance if needed, but the original uses static methods.
    # No explicit manager object required because all methods are classmethods/staticmethods.

    while True:
        choice = display_menu()
        if choice == "1":
            add_inventory(None)  # manager not needed, but kept for consistency
        elif choice == "2":
            view_inventories()
        elif choice == "3":
            delete_inventory()
        elif choice == "4":
            add_product()
        elif choice == "5":
            view_products()
        elif choice == "6":
            remove_product()
        elif choice == "7":
            update_stock()
        elif choice == "8":
            check_availability()
        elif choice == "9":
            transfer_stock()
        elif choice == "10":
            total_stock_report()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print_error("Invalid choice. Please enter a number from 0 to 10.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
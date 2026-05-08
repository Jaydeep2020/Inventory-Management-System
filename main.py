import streamlit as st
from services.manager import InventoryManager
from services.inventory import Inventory
from services.product import GroceryProduct, ElectricalProduct
from exception import (
    InventoryNotFoundException,
    ProductNotFoundException,
    InsufficientStockException
)

# =========================================================
# SESSION STATE
# =========================================================
if "manager" not in st.session_state:
    st.session_state.manager = InventoryManager()

manager = st.session_state.manager

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Inventory Management System",
    layout="wide"
)

st.title("📦 Inventory Management System")

# =========================================================
# HELPER FUNCTION
# =========================================================
def get_inventory(name, location):
    return manager.get_inventory(name, location)

# =========================================================
# SIDEBAR MENU
# =========================================================
menu = st.sidebar.selectbox(
    "Choose Operation",
    [
        "Add Inventory",
        "View Inventories",
        "Delete Inventory",
        "Add Product",
        "View Products",
        "Remove Product",
        "Update Stock",
        "Check Availability",
        # "Fulfill Order",
        "Transfer Stock",
        "Total Stock Report"
    ]
)

# =========================================================
# 1. ADD INVENTORY
# =========================================================
if menu == "Add Inventory":

    st.header("➕ Add Inventory")

    name = st.text_input("Inventory Name")
    location = st.text_input("Location")

    if st.button("Add Inventory"):

        try:
            inventory = Inventory(name, location)
            InventoryManager.add_inventory(inventory)

            st.success(
                f"Inventory '{name}' added successfully"
            )

        except Exception as e:
            st.error(str(e))

# =========================================================
# 2. VIEW INVENTORIES
# =========================================================
elif menu == "View Inventories":

    st.header("📋 All Inventories")

    inventories = InventoryManager.list_inventories()

    if not inventories:
        st.warning("No inventories found")

    else:
        for inv in inventories:

            with st.container(border=True):

                st.subheader(inv[1])

                st.write(f"**ID:** {inv[0]}")
                st.write(f"**Location:** {inv[2]}")

# =========================================================
# 3. DELETE INVENTORY
# =========================================================
elif menu == "Delete Inventory":

    st.header("🗑️ Delete Inventory")

    name = st.text_input("Inventory Name")
    location = st.text_input("Location")

    if st.button("Delete Inventory"):

        try:
            InventoryManager.remove_inventory(name, location)

            st.success(
                f"Inventory '{name}' deleted successfully"
            )

        except InventoryNotFoundException as e:
            st.error(str(e))

# =========================================================
# 4. ADD PRODUCT
# =========================================================
elif menu == "Add Product":

    st.header("➕ Add Product")

    inv_name = st.text_input("Inventory Name")
    inv_location = st.text_input("Inventory Location")

    product_type = st.selectbox(
        "Product Type",
        ["Grocery", "Electrical"]
    )

    product_name = st.text_input("Product Name")

    quantity = st.number_input(
        "Quantity",
        min_value=0,
        step=1
    )

    price = st.number_input(
        "Price",
        min_value=0.0
    )

    if product_type == "Grocery":

        expiry = st.date_input("Expiry Date")
        expiry = str(expiry)

    else:

        warranty_period = st.number_input(
            "Warranty (months)",
            min_value=0,
            step=1
        )

    if st.button("Add Product"):

        try:
            inventory_data = InventoryManager.get_inventory(
                inv_name,
                inv_location
            )

            if product_type == "Grocery":

                product = GroceryProduct(
                    product_name,
                    quantity,
                    price,
                    expiry
                )

            else:

                product = ElectricalProduct(
                    product_name,
                    quantity,
                    price,
                    warranty_period
                )

            Inventory.add_product(product, inventory_data[0])

            st.success(
                f"Product '{product_name}' added successfully"
            )

        except Exception as e:
            st.error(str(e))

# =========================================================
# 5. VIEW PRODUCTS
# =========================================================
elif menu == "View Products":

    st.header("📦 View Products")

    inv_name = st.text_input("Inventory Name")
    inv_location = st.text_input("Inventory Location")

    if st.button("View Products"):

        try:
            inventory = InventoryManager.get_inventory(
                inv_name,
                inv_location
            )

            products = Inventory.list_products(inventory[0])

            if not products:
                st.warning("No products found")

            else:

                import pandas as pd

                df = pd.DataFrame(
                    products,
                    columns=[
                        "Product Name",
                        "Category",
                        "Price",
                        "Expiry Date",
                        "Warranty (Months)",
                        "Quantity"
                    ]
                )

                st.dataframe(df, width="stretch")

        except Exception as e:
            st.error(str(e))
# =========================================================
# 6. REMOVE PRODUCT
# =========================================================
elif menu == "Remove Product":

    st.header("❌ Remove Product")

    inv_name = st.text_input("Inventory Name")
    inv_location = st.text_input("Inventory Location")

    product_name = st.text_input("Product Name")

    if st.button("Remove Product"):

        try:
            inventory_data = InventoryManager.get_inventory(
                inv_name,
                inv_location
            )

            Inventory.remove_product(product_name, inventory_data)

            st.success(
                f"Product '{product_name}' removed"
            )

        except ProductNotFoundException as e:
            st.error(str(e))

# =========================================================
# 7. UPDATE STOCK
# =========================================================
elif menu == "Update Stock":

    st.header("📈 Update Stock")

    inv_name = st.text_input("Inventory Name")
    inv_location = st.text_input("Inventory Location")

    product_name = st.text_input("Product Name")

    quantity = st.number_input(
        "Quantity (+ add / - remove)",
        step=1
    )

    if st.button("Update Stock"):

        try:
            inventory_data = InventoryManager.get_inventory(
                inv_name,
                inv_location
            )

            Inventory.update_stock(
                product_name,
                quantity,
                inventory_data
            )

            st.success(
                "Stock updated successfully"
            )

        except (
            ProductNotFoundException,
            InsufficientStockException
        ) as e:

            st.error(str(e))
        except Exception as e:
            st.error(str(e))

# =========================================================
# 8. CHECK AVAILABILITY
# =========================================================
elif menu == "Check Availability":

    st.header("🔍 Check Product Availability")

    inv_name = st.text_input("Inventory Name")
    inv_location = st.text_input("Inventory Location")

    product_name = st.text_input("Product Name")

    qty = st.number_input(
        "Required Quantity",
        min_value=1,
        step=1
    )

    if st.button("Check Availability"):

        try:
            inventory_data = InventoryManager.get_inventory(
                inv_name,
                inv_location
            )

            Inventory.check_availability(
                product_name,
                qty,
                inventory_data[0]
            )

            st.success(
                "Product is available"
            )

        except (
            ProductNotFoundException,
            InsufficientStockException
        ) as e:

            st.error(str(e))

# # =========================================================
# # 9. FULFILL ORDER
# # =========================================================
# elif menu == "Fulfill Order":
#
#     st.header("🛒 Fulfill Order")
#
#     product_name = st.text_input("Product Name")
#
#     qty = st.number_input(
#         "Quantity",
#         min_value=1,
#         step=1
#     )
#
#     if st.button("Fulfill Order"):
#
#         try:
#             manager.fulfill_order(
#                 product_name,
#                 qty
#             )
#
#             st.success(
#                 "Order fulfilled successfully"
#             )
#
#         except (
#             ProductNotFoundException,
#             InsufficientStockException
#         ) as e:
#
#             st.error(str(e))

# =========================================================
# 10. TRANSFER STOCK
# =========================================================
elif menu == "Transfer Stock":

    st.header("🔄 Transfer Stock")

    product_name = st.text_input("Product Name")

    qty = st.number_input(
        "Quantity",
        min_value=1,
        step=1
    )

    st.subheader("Source Inventory")

    source_name = st.text_input(
        "Source Inventory Name"
    )

    source_location = st.text_input(
        "Source Location"
    )

    st.subheader("Target Inventory")

    target_name = st.text_input(
        "Target Inventory Name"
    )

    target_location = st.text_input(
        "Target Location"
    )

    if st.button("Transfer Stock"):

        try:

            inventory_data = InventoryManager.get_inventory(
                source_name,
                source_location
            )

            inventory_data2 = InventoryManager.get_inventory(
                target_name,
                target_location
            )

            InventoryManager.transfer_stock(
                product_name,
                qty,
                inventory_data[0],
                inventory_data2[0]
            )

            st.success(
                "Stock transferred successfully"
            )

        except (
            InventoryNotFoundException,
            ProductNotFoundException,
            InsufficientStockException
        ) as e:

            st.error(str(e))

# =========================================================
# 11. TOTAL STOCK REPORT
# =========================================================
elif menu == "Total Stock Report":

    st.header("📊 Total Stock Report")

    product_name = st.text_input("Product Name")

    if st.button("Get Total Stock"):

        total = InventoryManager.get_total_stock(product_name)

        st.info(
            f"Total stock for '{product_name}' = {total}"
        )












# # from services.manager import InventoryManager
# # from services.inventory import Inventory
# # from services.product import GroceryProduct, ElectricalProduct
# # from exception import (
# #     InventoryNotFoundException,
# #     ProductNotFoundException,
# #     InsufficientStockException
# # )
# #
# # def print_menu():
# #     print("\n========== Inventory Management System ==========")
# #
# #     print("\n--- Inventory Operations ---")
# #     print("1. Add Inventory")
# #     print("2. View Inventories")
# #     print("3. Delete Inventory")
# #
# #     print("\n--- Product Operations ---")
# #     print("4. Add Product to Inventory")
# #     print("5. View Products in Inventory")
# #     print("6. Remove Product from Inventory")
# #
# #     print("\n--- Stock Operations ---")
# #     print("7. Add / Update Stock")
# #     print("8. Check Product Availability")
# #
# #     print("\n--- Order & Transfer ---")
# #     print("9. Fulfill Order")
# #     print("10. Transfer Stock")
# #
# #     print("\n--- Reports ---")
# #     print("11. Get Total Stock Across Inventories")
# #
# #     print("\n--- Exit ---")
# #     print("12. Exit")
# #
# # def get_valid_input(prompt, converter=str, error_msg="Invalid input. Please try again."):
# #     """Repeatedly ask for input until conversion succeeds."""
# #     while True:
# #         try:
# #             user_input = input(prompt)
# #             return converter(user_input)
# #         except ValueError:
# #             print(f"❌ {error_msg}")
# #
# # def get_inventory_by_name(manager, prompt="Enter inventory name: ", prompt2 = "Enter Location: "):
# #     """Retry getting an inventory until a valid name is provided."""
# #     while True:
# #         try:
# #             name = input(prompt)
# #             location = input(prompt2)
# #             return manager.get_inventory(name, location)
# #         except InventoryNotFoundException as e:
# #             print(f"❌ {e}")
# #             print("Please enter an existing inventory name / location.")
# #
# # def main():
# #     manager = InventoryManager()
# #
# #     while True:
# #         print_menu()
# #         choice = get_valid_input("\nEnter your choice: ", int, "Please enter a number between 1-12.")
# #
# #         # ---------- INVENTORY OPERATIONS ----------
# #         if choice == 1:
# #             name = input("Enter inventory name: ")
# #             location = input("Enter location: ")
# #             inventory = Inventory(name, location)
# #             manager.add_inventory(inventory)
# #             print(f"✅ Inventory '{name}' added successfully")
# #
# #         elif choice == 2:
# #             inventories = manager.list_inventories()
# #             if not inventories:
# #                 print("⚠️ No inventories found")
# #             else:
# #                 for inv in inventories:
# #                     print(f"\nID: {inv.inventory_id}\nName: {inv.name}\nLocation: {inv.location}")
# #
# #         elif choice == 3:
# #             name = input("Enter inventory name to delete: ")
# #             location = input("Enter location: ")
# #             try:
# #                 manager.remove_inventory(name, location)
# #                 print(f"❌ Inventory '{name}' deleted successfully")
# #             except InventoryNotFoundException as e:
# #                 print(f"❌ {e}")
# #
# #         # ---------- PRODUCT OPERATIONS ----------
# #         elif choice == 4:   # Add product to inventory
# #             inventory = get_inventory_by_name(manager, "Enter inventory name: ", "Enter Location: ")
# #
# #             # Product type selection with retry
# #             product_type = get_valid_input(
# #                 "Enter product type:\n1) Grocery Product\n2) Electrical Product\nYour choice: ",
# #                 int, "Enter 1 or 2."
# #             )
# #             while product_type not in (1, 2):
# #                 print("❌ Invalid choice. Enter 1 for Grocery, 2 for Electrical.")
# #                 product_type = get_valid_input("Your choice: ", int, "Enter 1 or 2.")
# #
# #             name = input("Enter product name: ")
# #             quantity = get_valid_input("Enter quantity: ", int, "Quantity must be an integer.")
# #             price = get_valid_input("Enter price: ", float, "Price must be a number.")
# #
# #             try:
# #                 if product_type == 1:
# #                     expiry = input("Enter expiry date (YYYY-MM-DD): ")
# #                     product = GroceryProduct(name, quantity, price, expiry)
# #                 else:
# #                     warranty = get_valid_input("Enter warranty period (months): ", int, "Warranty must be an integer.")
# #                     product = ElectricalProduct(name, quantity, price, warranty)
# #
# #                 inventory.add_product(product)
# #                 print(f"✅ Product '{name}' added to inventory '{inventory.name}'")
# #             except Exception as e:
# #                 print(f"❌ Failed to add product: {e}")
# #
# #         elif choice == 5:   # View products
# #             inventory = get_inventory_by_name(manager, "Enter inventory name: ", "Enter Location: ")
# #             products = inventory.list_products()
# #             if not products:
# #                 print("⚠️ No products found")
# #             else:
# #                 for product in products:
# #                     print(product)
# #                     print()
# #
# #         elif choice == 6:   # Remove product
# #             inventory = get_inventory_by_name(manager, "Enter inventory name: ", "Enter Location: ")
# #             product_name = input("Enter product name to remove: ")
# #             try:
# #                 inventory.remove_product(product_name)
# #                 print(f"✅ Product '{product_name}' removed")
# #             except ProductNotFoundException as e:
# #                 print(f"❌ {e}")
# #
# #         # ---------- STOCK OPERATIONS ----------
# #         elif choice == 7:   # Update stock
# #             inventory = get_inventory_by_name(manager, "Enter inventory name: ", "Enter Location: ")
# #             product_name = input("Enter product name: ")
# #             quantity = get_valid_input("Enter quantity (+add / -remove): ", int, "Quantity must be an integer.")
# #             try:
# #                 inventory.update_stock(product_name, quantity)
# #                 print("✅ Stock updated successfully")
# #             except (ProductNotFoundException, InsufficientStockException) as e:
# #                 print(f"❌ {e}")
# #
# #         elif choice == 8:   # Check availability
# #             inventory = get_inventory_by_name(manager, "Enter inventory name: ", "Enter Location: ")
# #             product_name = input("Enter product name: ")
# #             qty = get_valid_input("Enter required quantity: ", int, "Quantity must be an integer.")
# #             try:
# #                 inventory.check_availability(product_name, qty)
# #                 print("✅ Product is available")
# #             except (ProductNotFoundException, InsufficientStockException) as e:
# #                 print(f"❌ {e}")
# #
# #         # ---------- ORDER & TRANSFER ----------
# #         elif choice == 9:   # Fulfill order
# #             product_name = input("Enter product name: ")
# #             qty = get_valid_input("Enter quantity: ", int, "Quantity must be an integer.")
# #             try:
# #                 manager.fulfill_order(product_name, qty)
# #                 print("✅ Order fulfilled")
# #             except (ProductNotFoundException, InsufficientStockException) as e:
# #                 print(f"❌ {e}")
# #
# #         elif choice == 10:  # Transfer stock
# #             product_name = input("Enter product name: ")
# #             qty = get_valid_input("Enter quantity: ", int, "Quantity must be an integer.")
# #             source_name = input("Enter source inventory: ")
# #             source_location = input("Enter source location: ")
# #             target_name = input("Enter target inventory: ")
# #             target_location = input("Enter target location: ")
# #             try:
# #                 manager.transfer_stock(product_name, qty, source_name, source_location, target_name, target_location)
# #                 print("✅ Stock transferred")
# #             except (InventoryNotFoundException, ProductNotFoundException, InsufficientStockException) as e:
# #                 print(f"❌ {e}")
# #
# #         # ---------- REPORTS ----------
# #         elif choice == 11:  # Total stock
# #             product_name = input("Enter product name: ")
# #             total = manager.get_total_stock(product_name)
# #             print(f"📊 Total stock for '{product_name}' = {total}")
# #
# #         elif choice == 12:
# #             print("👋 Exiting system...")
# #             break
# #
# #         else:
# #             print("❌ Invalid choice. Please select 1-12.")
# #
# # if __name__ == "__main__":
# #     main()
#
#
#
# #
# #
# #
#
# from manager import InventoryManager
# from inventory import Inventory
# from product import GroceryProduct, ElectricalProduct
# from exception import (
#     InventoryNotFoundException,
#     ProductNotFoundException,
#     InsufficientStockException
# )
#
#
# def print_menu():
#     print("\n========== Inventory Management System ==========")
#
#     print("\n--- Inventory Operations ---")
#     print("1. Add Inventory")
#     print("2. View Inventories")
#     print("3. Delete Inventory")
#
#     print("\n--- Product Operations ---")
#     print("4. Add Product to Inventory")
#     print("5. View Products in Inventory")
#     print("6. Remove Product from Inventory")
#
#     print("\n--- Stock Operations ---")
#     print("7. Add / Update Stock")
#     print("8. Check Product Availability")
#
#     print("\n--- Order & Transfer ---")
#     print("9. Fulfill Order")
#     print("10. Transfer Stock")
#
#     print("\n--- Reports ---")
#     print("11. Get Total Stock Across Inventories")
#
#     print("\n--- Exit ---")
#     print("12. Exit")
#
#
# def main():
#     manager = InventoryManager()
#
#     while True:
#         try:
#             print_menu()
#             choice = int(input("\nEnter your choice: "))
#
#             # ---------------- INVENTORY ----------------
#             if choice == 1:
#                 name = input("Enter inventory name: ")
#                 location = input("Enter location: ")
#
#                 inventory = Inventory(name, location)
#                 manager.add_inventory(inventory)
#
#                 print(f"✅ Inventory '{name}' added successfully")
#
#             elif choice == 2:
#                 inventories = manager.list_inventories()
#
#                 if not inventories:
#                     print("⚠️ No inventories found")
#                 else:
#                     for inv in inventories:
#                         print(f"\nID: {inv.inventory_id}")
#                         print(f"Name: {inv.name}")
#                         print(f"Location: {inv.location}")
#
#             elif choice == 3:
#                 name = input("Enter inventory name to delete: ")
#                 manager.remove_inventory(name)
#
#                 print(f"❌ Inventory '{name}' deleted successfully")
#
#             # ---------------- PRODUCT ----------------
#             elif choice == 4:
#                 inv_name = input("Enter inventory name: ")
#                 inventory = manager.get_inventory(inv_name)
#                 # print(inventory)
#                 product_type = input("""Enter product type:
#     1) Grocery Product
#     2) Electrical or Other Product
#     Enter your choice: """)
#                 name = input("Enter product name: ")
#                 quantity = int(input("Enter quantity: "))
#                 price = float(input("Enter price: "))
#                 if product_type == "1":
#                     expiry = input("Enter expiry date: ")
#                     product = GroceryProduct(name, quantity, price, expiry)
#                     # print(product)
#                     inventory.add_product(product)
#                 elif product_type == "2":
#                     warranty = int(input("Enter warranty period (months): "))
#                     product = ElectricalProduct(name, quantity, price, warranty)
#                     inventory.add_product(product)
#                 else:
#                     print("Invalid Choice, choose again...")
#
#             elif choice == 5:
#                 inv_name = input("Enter inventory name: ")
#                 inventory = manager.get_inventory(inv_name)
#                 # print(inventory)
#                 products = inventory.list_products()
#
#                 if not products:
#                     print("⚠️ No products found")
#                 else:
#                     for product in products:
#                         print(product)
#                         print()
#
#             elif choice == 6:
#                 inv_name = input("Enter inventory name: ")
#                 product_name = input("Enter product name to remove: ")
#
#                 inventory = manager.get_inventory(inv_name)
#                 inventory.remove_product(product_name)
#
#             # ---------------- STOCK ----------------
#             elif choice == 7:
#                 inv_name = input("Enter inventory name: ")
#                 product_name = input("Enter product name: ")
#                 quantity = int(input("Enter quantity (+add / -remove): "))
#
#                 inventory = manager.get_inventory(inv_name)
#                 inventory.update_stock(product_name, quantity)
#
#                 print("✅ Stock updated successfully")
#
#             elif choice == 8:
#                 inv_name = input("Enter inventory name: ")
#                 product_name = input("Enter product name: ")
#                 qty = int(input("Enter required quantity: "))
#
#                 inventory = manager.get_inventory(inv_name)
#                 inventory.check_availability(product_name, qty)
#
#                 print("✅ Product is available")
#
#             # ---------------- ORDER ----------------
#             elif choice == 9:
#                 product_name = input("Enter product name: ")
#                 qty = int(input("Enter quantity: "))
#
#                 manager.fulfill_order(product_name, qty)
#
#             elif choice == 10:
#                 product_name = input("Enter product name: ")
#                 qty = int(input("Enter quantity: "))
#                 source = input("Enter source inventory: ")
#                 target = input("Enter target inventory: ")
#
#                 manager.transfer_stock(product_name, qty, source, target)
#
#             # ---------------- REPORT ----------------
#             elif choice == 11:
#                 product_name = input("Enter product name: ")
#                 total = manager.get_total_stock(product_name)
#
#                 print(f"📊 Total stock for '{product_name}' = {total}")
#
#             # ---------------- EXIT ----------------
#             elif choice == 12:
#                 print("👋 Exiting system...")
#                 break
#
#             else:
#                 print("❌ Invalid choice")
#
#         # ---------------- EXCEPTION HANDLING ----------------
#         except ValueError:
#             print("❌ Invalid input. Please enter correct data type.")
#
#         except InventoryNotFoundException as e:
#             print(f"❌ {e}")
#
#         except ProductNotFoundException as e:
#             print(f"❌ {e}")
#
#         except InsufficientStockException as e:
#             print(f"❌ {e}")
#
#         except Exception as e:
#             print(f"⚠️ Unexpected error: {e}")
#
#
# if __name__ == "__main__":
#     main()
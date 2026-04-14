from inventory import Inventory
from exception import InsufficientStockException, InventoryNotFoundException, ProductNotFoundException


class InventoryManager:
    def __init__(self):
        self.inventories = {}

    def add_inventory(self, inventory: Inventory):
        self.inventories[inventory.name] = inventory

    def remove_inventory(self, inventory_name: str):
        if inventory_name not in self.inventories:
            raise InventoryNotFoundException(inventory_name)
        del self.inventories[inventory_name]

    def get_inventory(self, inventory_name: str):
        if inventory_name not in self.inventories:
            raise InventoryNotFoundException(inventory_name)
        return self.inventories[inventory_name]

    def list_inventories(self):
        return list(self.inventories.values())

    def get_total_stock(self, product_name: str):
        total = 0
        for inventory in self.inventories.values():
            try:
                product = inventory.get_product(product_name)
                total += product.quantity
            except ProductNotFoundException:
                continue
        return total

    def fulfill_order(self, product_name: str, required_quantity: int):
        remaining = required_quantity
        total_available = self.get_total_stock(product_name)

        if total_available < required_quantity:
            raise InsufficientStockException(product_name, required_quantity, total_available)

        for inventory in self.inventories.values():
            if remaining <= 0:
                break

            reserved = inventory.reserve_stock(product_name, remaining)
            remaining -= reserved

        print(f"Order fulfilled for '{product_name}' with quantity {required_quantity}")

    def transfer_stock(self, product_name: str, quantity: int, source_inventory: str, target_inventory: str):
        source = self.get_inventory(source_inventory)
        target = self.get_inventory(target_inventory)

        reserved = source.reserve_stock(product_name, quantity)

        if reserved == 0:
            raise InsufficientStockException(product_name, quantity, 0)

        target.update_stock(product_name, reserved)

        print(f"Transferred {reserved} of '{product_name}' from {source_inventory} to {target_inventory}")


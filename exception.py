class InventoryException(Exception):
    """Base class for inventory-related exceptions"""
    pass

class ProductNotFoundException(InventoryException):
    def __init__(self, product_name, inventory_name):
        self.product_name = product_name
        self.inventory_name = inventory_name
        super().__init__(f"Product '{product_name}' not found in Inventory '{inventory_name}'")

class InsufficientStockException(InventoryException):
    def __init__(self, product_name, required, available):
        self.product_name = product_name
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient stock for '{product_name}'. Required: {required}, Available: {available}"
        )

class InventoryNotFoundException(InventoryException):
    def __init__(self, inventory_name):
        self.inventory_name = inventory_name
        super().__init__(f"Inventory '{inventory_name}' not found")

from product import Product
from exception import ProductNotFoundException, InsufficientStockException

class Inventory:
    counter = 0

    def __init__(self, name: str):
        self.inventory_id = Inventory.counter
        self.name = name
        self.products = {}
        Inventory.counter += 1

    def add_product(self, product: Product):
        if product.name in self.products:
            self.products[product.name].increase_stock(product.quantity)
        else:
            self.products[product.name] = product

    def remove_product(self, product_name: str):
        if product_name not in self.products:
            raise ProductNotFoundException(product_name, self.name)
        del self.products[product_name]

    def get_product(self, product_name: str):
        if product_name not in self.products:
            raise ProductNotFoundException(product_name, self.name)
        return self.products[product_name]

    def update_stock(self, product_name: str, quantity: int):
        product = self.get_product(product_name)
        if quantity >= 0:
            product.increase_stock(quantity)
        else:
            product.decrease_stock(abs(quantity))
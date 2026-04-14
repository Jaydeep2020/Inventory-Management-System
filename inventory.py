from exception import ProductNotFoundException, InsufficientStockException
from product import Product
import exception

class Inventory:
    _id_counter = 1
    def __init__(self, name, location):
        self.inventory_id = Inventory._id_counter
        self.name = name
        self.location = location
        self.products = {}
        Inventory._id_counter += 1

    def add_product(self, product: Product):
        if product.name not in self.products:
            self.products[product.name] = product

        self.products[product.name].quantity += product.quantity

        # ✅ Acknowledgment message
        print(f"✅ STOCK ADDED: {product.quantity} {product.name}(s) added to {self.name}")

    def remove_product(self, product_name: str):
        if product_name not in self.products:
            raise ProductNotFoundException(product_name, self.name)

        del self.products[product_name]

        # ✅ Acknowledgment message
        print(f"❌ PRODUCT REMOVED: {product_name} removed from {self.name}")

    def get_product(self, product_name: str) -> Product:
        if product_name not in self.products:
            raise ProductNotFoundException(product_name, self.name)
        return self.products[product_name]

    def update_stock(self, product_name: str, quantity: int):
        product = self.get_product(product_name)
        if quantity > 0:
            product.increase_stock(quantity)
        else:
            product.decrease_stock(abs(quantity))

    def check_availability(self, product_name: str, required_quantity: int):
        product = self.get_product(product_name)
        return product.is_available(required_quantity)

    def list_products(self):
        return list(self.products.values())

    def reserve_stock(self, product_name: str, quantity: int):
        """Take whatever stock is available, even if it’s not enough"""
        if product_name not in self.products:
            return 0

        product = self.products[product_name]
        available = product.quantity

        if available >= quantity:
            product.decrease_stock(quantity)
            return quantity
        else:
            product.decrease_stock(available)
            return available


    def __str__(self):
        return f"Inventory: {self.name}, Products: {[str(p) for p in self.products.values()]}"






#
# p = Product('shoes', 2, 2000, 'footwear')
#
# i = Inventory('Zepto', 'Ahemdabad')
# i.add_product(p)
# print(i)
# print(i.products['shoes'])
# try:
#     i.remove_product('shoes')
#     i.get_product('shoes')
#
#
# except (ProductNotFoundException, KeyError) as e:
#     print(f"Error : {e}")
#
# except exception as e:
#     print("Error : ", e)
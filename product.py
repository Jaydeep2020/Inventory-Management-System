from exception import InsufficientStockException

class Product:
    _id_counter = 1
    def __init__(self, name: str, quantity: int, price: float, category: str):
        self.product_id = Product._id_counter
        self.name = name
        self.quantity = quantity
        self.price = price
        self.category = category
        Product._id_counter += 1

    def increase_stock(self, amount: int):
        """Add stock to product"""
        self.quantity += amount


    def decrease_stock(self, amount: int):
        """Reduce stock from product"""
        self.quantity -= amount

    def is_available(self, required_quantity: int) -> bool:
        """check if required quantity is available"""
        if required_quantity > self.quantity:
            raise InsufficientStockException(self.name, required_quantity, self.quantity)
        return True

    def __str__(self):
        return f"""Product_Id : {self.product_id}
Product : {self.name}
Quantity: {self.quantity}
Price: {self.price}"""

# p = Product('Shoes', 4, 3500, 'footwear')
# print(p)
# try:
#     print(p.is_available(5))
# except InsufficientStockException as e:
#     print("Error : ", e)
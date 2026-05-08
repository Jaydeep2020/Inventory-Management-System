from abc import ABC, abstractmethod
from exception import InsufficientStockException
from logs.logger_config import get_logger

logger = get_logger(__name__)

class Product(ABC):
    _id_counter = 1

    def __init__(self, name: str, quantity: int, price: float, category: str):
        self._product_id = Product._id_counter
        self._name = name
        self._quantity = quantity
        self._price = price
        self._category = category
        Product._id_counter += 1

        logger.info(
            f"Product created | ID: {self._product_id}, Name: {self._name}, "
            f"Qty: {self._quantity}, Price: {self._price}, Category: {self._category}"
        )

    # Getters (read-only for some)
    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def quantity(self):
        return self._quantity

    @property
    def price(self):
        return self._price

    @property
    def category(self):
        return self._category

    @quantity.setter
    def quantity(self, value):
        if value < 0:
            logger.error(f"Invalid quantity update attempt for {self._name}: {value}")
            raise ValueError("Quantity cannot be negative")
        logger.info(f"Quantity updated | {self._name}: {self._quantity} -> {value}")
        self._quantity = value

    @price.setter
    def price(self, value):
        if value < 0:
            logger.error(f"Invalid price update attempt for {self._name}: {value}")
            raise ValueError("Price cannot be negative")
        logger.info(f"Price updated | {self._name}: {self._price} -> {value}")
        self._price = value

    def increase_stock(self, amount: int):
        if amount <= 0:
            logger.error(f"Invalid stock increase attempt for {self._name}: {amount}")
            raise ValueError("Stock Quantity cannot be negative")
        old_qty = self._quantity
        self._quantity += amount

        logger.info(
            f"Stock increased | {self._name}: {old_qty} -> {self._quantity} (+{amount})"
        )

    def decrease_stock(self, amount: int):
        if amount <= 0:
            logger.error(f"Invalid stock decrease attempt for {self._name}: {amount}")
            raise ValueError("Amount must be positive")

        if amount > self._quantity:
            logger.warning(
                f"Insufficient stock | {self._name}: Requested={amount}, Available={self._quantity}"
            )
            raise InsufficientStockException(self._name, amount, self._quantity)

        old_qty = self._quantity
        self._quantity -= amount

        logger.info(
            f"Stock decreased | {self._name}: {old_qty} -> {self._quantity} (-{amount})"
        )

    def is_available(self, required_quantity: int) -> bool:
        if required_quantity > self._quantity:
            logger.warning(
                f"Stock check failed | {self._name}: Required={required_quantity}, Available={self._quantity}"
            )
            raise InsufficientStockException(
                self._name, required_quantity, self._quantity
            )

        logger.debug(
            f"Stock available | {self._name}: Required={required_quantity}, Available={self._quantity}"
        )
        return True

    # The single abstract method – each subclass must implement its own tax calculation
    @abstractmethod
    def calculate_tax(self) -> float:
        """Return the tax amount for this product (based on product-specific rules)."""
        pass

    def __str__(self):
        return f"""Product_Id : {self._product_id}
Product : {self._name}
Quantity: {self._quantity}
Price: {self._price}
Category: {self._category}"""


# ---------- SUBCLASS: ELECTRICAL PRODUCT ----------
class GroceryProduct(Product):
    def __init__(self, name: str, quantity: int, price: float, expiry_date: str):
        super().__init__(name, quantity, price, category="Grocery")
        self._expiry_date = expiry_date
        logger.info(f"Grocery product initialized: (ID: {self._product_id} | Name: {self._name} | Qty: {self._quantity} | Category: {self._category} | Price: {self._price} | Expiry: {self._expiry_date})")

    @property
    def expiry_date(self):
        return self._expiry_date

    # Implement the abstract method: groceries may have a lower tax rate (e.g., 5%)
    def calculate_tax(self) -> float:
        tax = self.price * 0.05
        logger.debug(f"Tax calculated (Grocery) | {self._name}: {tax}")
        return tax

    # Polymorphism: override __str__ to include expiry date
    def __str__(self):
        return super().__str__() + f"\nExpiry Date: {self._expiry_date}\nTax: {self.calculate_tax():.2f}"

# ---------- SUBCLASS: ELECTRICAL PRODUCT ----------
class ElectricalProduct(Product):
    def __init__(self, name: str, quantity: int, price: float, warranty_period: int):
        super().__init__(name, quantity, price, category="Electrical")
        self._warranty_period = warranty_period
        logger.info(
            f"Electrical product initialized | ID: {self._product_id}, Warranty: {self._warranty_period} months"
        )

    @property
    def warranty_period(self):
        return self._warranty_period

    # Implement the abstract method: electrical products may have a higher tax rate (e.g., 18%)
    def calculate_tax(self) -> float:
        tax = self.price * 0.18
        logger.debug(f"Tax calculated (Electrical) | {self._name}: {tax}")
        return tax


    # Polymorphism: override __str__ to include warranty period
    def __str__(self):
        return super().__str__() + f"\nWarranty Period: {self._warranty_period}\nTax: {self.calculate_tax():.2f}"


# e = ElectricalProduct("Laptop", 10, 40000, 6)
# print(e)
# print()
# g = GroceryProduct("Mango", 20, 50, "20/04/2026")
# print(g)


# p = Product('Shoes', 4, 3500, 'footwear')
# print(p)
# try:
#     print(p.is_available(5))
# except InsufficientStockException as e:
#     print("Error : ", e)
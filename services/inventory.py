from exception import ProductNotFoundException
from services.product import Product
from logs.logger_config import get_logger
from db.db_connection import get_cursor

logger = get_logger(__name__)

class Inventory:
    _id_counter = 1
    def __init__(self, name, location, inventory_id=None):
        self._inventory_id = inventory_id
        self._name = name
        self._location = location
        self.products = {}   # private dictionary (name -> Product)
        Inventory._id_counter += 1
        logger.info(
            f"Inventory created | ID: {self._inventory_id}, Name: {self._name}, Location: {self._location}"
        )

    # ---------- Properties (Encapsulation) ----------
    @property
    def inventory_id(self):
        return self._inventory_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def location(self) -> str:
        return self._location

    # @property
    # def products(self):
    #     """Return a copy to prevent external modification"""
    #     return self.products.copy()

    @staticmethod
    def add_product(product: Product, inventory_id):

        try:
            with get_cursor() as cursor:

                # check if product exists
                check_query = """
                SELECT id FROM product WHERE name = %s AND category = %s
                """
                values1 = (product.name, product.category)
                cursor.execute(check_query,values1)

                existing_product = cursor.fetchone()

                # product already exists
                if existing_product:

                    product_id = existing_product[0]

                    update_stock = """
                    update inventory_stock 
                    set quantity = quantity + %s
                    where inventory_id = %s and product_id = %s
                    """
                    values2 = (product.quantity, inventory_id, product_id)

                    cursor.execute(update_stock, values2)

                    logger.info(
                        f"Updated stock | Product: {product.name} | "
                        f"Added Quantity: {product.quantity}"
                    )

                    return

                # Add new product
                if product.category == 'Grocery':
                    insert_product_query = """
                    insert into product (name, category, price, expiry_date)
                    values (%s, %s, %s, %s)
                    returning id
                    """
                    values3 = (product.name, product.category, product.price, product.expiry)

                    cursor.execute(insert_product_query, values3)

                else:
                    insert_product_query = """
                                        insert into product (name, category, price, warranty_months)
                                        values (%s, %s, %s, %s)
                                        returning id
                                        """
                    values3 = (product.name, product.category, product.price, product.warranty_period)

                cursor.execute(insert_product_query, values3)

                product_id = cursor.fetchone()[0]

                # Insert inventory stock
                insert_stock_query = """
                insert into inventory_stock (inventory_id, product_id, quantity)
                values (%s, %s, %s)
                """
                values4 = (inventory_id, product_id, product.quantity)
                cursor.execute(insert_stock_query, values4)

                logger.info(
                    f"Product added successfully | "
                    f"Product: {product.name}"
                )

        except Exception as e:

            logger.exception(
                f"Failed to add product | Error: {str(e)}"
            )

            raise

    @staticmethod
    def remove_product(product_name: str, inventory_data):
        """Remove a product completely from inventory."""

        query = """
        SELECT id FROM product WHERE name = %s
        """

        delete_query = """
        DELETE FROM inventory_stock
        WHERE inventory_id = %s AND product_id = %s
        """

        try:

            with get_cursor() as cursor:

                cursor.execute(query, (product_name,))
                product_id = cursor.fetchone()[0]

                values = (inventory_data[0], product_id)

                cursor.execute(delete_query, values)

                if cursor.rowcount == 0:
                    logger.error(
                        f"Remove failed | Product not found | "
                        f"Product: {product_name}"
                    )

                    raise ProductNotFoundException(product_name, inventory_data[1])

                logger.info(
                    f"Product removed successfully | "
                    f"Product: {product_name}"
                )

        except ProductNotFoundException:
            raise

        except Exception as e:

            logger.exception(
                f"Failed to remove product | Error: {str(e)}"
            )

            raise

    def get_product(self, product_name: str) -> Product:
        """Retrieve a product by name."""
        if product_name not in self.products:
            logger.error(
                f"Fetch failed | Inventory: {self._name}, Product: {product_name} not found"
            )
            raise ProductNotFoundException(product_name, self.name)

        logger.debug(
            f"Product fetched | Inventory: {self._name}, Product: {product_name}"
        )
        return self.products[product_name]

    def update_stock(self, product_name: str, quantity: int):
        """Update stock: positive quantity increases stock, negative decreases."""
        product = self.get_product(product_name)
        if quantity > 0:
            old_qty = product.quantity
            product.increase_stock(quantity)

            logger.info(
                f"Stock increased | Inventory: {self._name}, Product: {product_name}, "
                f"{old_qty} -> {product.quantity} (+{quantity})"
            )
        else:
            old_qty = product.quantity
            product.decrease_stock(abs(quantity))

            logger.info(
                f"Stock decreased | Inventory: {self._name}, Product: {product_name}, "
                f"{old_qty} -> {product.quantity} (-{abs(quantity)})"
            )

    def check_availability(self, product_name: str, required_quantity: int):
        """
        Check if a product has enough stock.
        Returns True if available, otherwise raises InsufficientStockException.
        """
        product = self.get_product(product_name)
        logger.debug(
            f"Checking availability | Inventory: {self._name}, Product: {product_name}, "
            f"Required: {required_quantity}, Available: {product.quantity}"
        )
        return product.is_available(required_quantity)

    @staticmethod
    def list_products(inventory_id):
        """Return a list of all products in the inventory."""
        query = """
        SELECT p.name, p.category, p.price, p.expiry_date, p.warranty_months, s.quantity
        from inventory_stock s
        join product p on p.id = s.product_id
        where s.inventory_id = %s
        """
        
        with get_cursor() as cursor:
            cursor.execute(query, (inventory_id,))
            product_list = cursor.fetchall()
            
            return product_list

    def reserve_stock(self, product_name: str, quantity: int):
        """Take whatever stock is available, even if it’s not enough"""
        if product_name not in self.products:
            logger.warning(
                f"Reserve failed | Inventory: {self._name}, Product: {product_name} not found"
            )
            return 0

        product = self.products[product_name]
        available = product.quantity

        if available >= quantity:
            product.decrease_stock(quantity)

            logger.info(
                f"Stock reserved | Inventory: {self._name}, Product: {product_name}, "
                f"Reserved: {quantity}"
            )
            return quantity
        else:
            product.decrease_stock(available)

            logger.warning(
                f"Partial reserve | Inventory: {self._name}, Product: {product_name}, "
                f"Requested: {quantity}, Reserved: {available}"
            )
            return available


    def __str__(self):
        return f"Inventory: {self.name}, Products: {[str(p) for p in self.products.values()]}"

    # # ---------- Utility ----------
    #     # def __str__(self) -> str:
    #     #     product_summary = ", ".join([f"{p.name}({p.quantity})" for p in self._products.values()])
    #     #     return f"Inventory(ID:{self._inventory_id}, Name:{self._name}, Location:{self._location}, Products:[{product_summary}])"

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

l = Inventory.list_products(5)
print(l)
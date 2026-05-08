from exception import ProductNotFoundException, InsufficientStockException
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

                # Check if product exists
                check_query = """
                SELECT id
                FROM product
                WHERE name = %s AND category = %s
                """

                values1 = (product.name, product.category)

                cursor.execute(check_query, values1)

                existing_product = cursor.fetchone()

                # Product exists
                if existing_product:

                    product_id = existing_product[0]

                # Product does not exist
                else:

                    if product.category == 'Grocery':

                        insert_product_query = """
                        INSERT INTO product
                        (name, category, price, expiry_date)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """

                        values2 = (
                            product.name,
                            product.category,
                            product.price,
                            product.expiry_date
                        )

                    else:

                        insert_product_query = """
                        INSERT INTO product
                        (name, category, price, warranty_months)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id
                        """

                        values2 = (
                            product.name,
                            product.category,
                            product.price,
                            product.warranty_period
                        )

                    cursor.execute(insert_product_query, values2)

                    product_id = cursor.fetchone()[0]

                # Check stock row exists
                stock_query = """
                SELECT quantity
                FROM inventory_stock
                WHERE inventory_id = %s AND product_id = %s
                """

                values3 = (inventory_id, product_id)

                cursor.execute(stock_query, values3)

                existing_stock = cursor.fetchone()

                # Stock exists -> update
                if existing_stock:

                    update_query = """
                    UPDATE inventory_stock
                    SET quantity = quantity + %s
                    WHERE inventory_id = %s AND product_id = %s
                    """

                    values4 = (
                        product.quantity,
                        inventory_id,
                        product_id
                    )

                    cursor.execute(update_query, values4)

                # Stock does not exist -> insert
                else:

                    insert_stock_query = """
                    INSERT INTO inventory_stock
                    (inventory_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    """

                    values5 = (
                        inventory_id,
                        product_id,
                        product.quantity
                    )

                    cursor.execute(insert_stock_query, values5)

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

    @staticmethod
    def update_stock(
            product_name: str,
            quantity: int,
            inventory_id: int
    ):
        """Update stock quantity for a product in an inventory."""

        get_product_query = """
        SELECT id
        FROM product
        WHERE name = %s
        """

        update_stock_query = """
        UPDATE inventory_stock
        SET quantity = quantity + %s
        WHERE inventory_id = %s
          AND product_id = %s
        """

        try:

            if quantity <= 0:
                raise ValueError(
                    "Quantity must be greater than 0"
                )

            with get_cursor() as cursor:

                # Fetch product ID
                cursor.execute(
                    get_product_query,
                    (product_name,)
                )

                product = cursor.fetchone()

                if product is None:
                    raise ValueError(
                        f"Product '{product_name}' not found"
                    )

                product_id = product[0]

                # Update stock
                values = (
                    quantity,
                    inventory_id,
                    product_id
                )

                cursor.execute(
                    update_stock_query,
                    values
                )

                if cursor.rowcount == 0:
                    raise ValueError(
                        "Product not found in inventory"
                    )

                logger.info(
                    f"Stock updated successfully | "
                    f"Product: {product_name} | "
                    f"Added Quantity: {quantity}"
                )

        except Exception as e:

            logger.exception(
                f"Failed to update stock | Error: {str(e)}"
            )

            raise

    @staticmethod
    def check_availability(product_name: str, required_quantity: int, inventory_id: int):

        query = """
        SELECT s.quantity
        FROM inventory_stock s
        JOIN product p
            ON p.id = s.product_id
        WHERE p.name = %s
        AND s.inventory_id = %s
        """

        with get_cursor() as cursor:

            values = (product_name, inventory_id)

            cursor.execute(query, values)

            stock = cursor.fetchone()

            if stock is None:
                raise ProductNotFoundException(
                    f"{product_name} not found in inventory"
                )

            available_quantity = stock[0]

            if available_quantity < required_quantity:
                raise InsufficientStockException(product_name, required_quantity, available_quantity)

            return True


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

# l = Inventory.list_products(5)
# print(l)
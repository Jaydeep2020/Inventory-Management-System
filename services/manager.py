from db.db_connection import get_cursor
# from main import inventory
from services.inventory import Inventory
from exception import InsufficientStockException, InventoryNotFoundException, ProductNotFoundException
from logs.logger_config import get_logger

logger = get_logger(__name__)

class InventoryManager:
    def __init__(self):
        logger.info("InventoryManager initialized")

    @staticmethod
    def add_inventory(inventory: Inventory):

        query = """
        INSERT INTO inventory(name, location)
        VALUES (%s, %s)
        """
        values = (inventory.name, inventory.location)
        with get_cursor() as cursor:
            try:
                cursor.execute(query, values)
                logger.info(
                    f"Inventory added | Name: {inventory.name}, Location: {inventory.location}"
                )
            except Exception:
                raise Exception("Inventory already exists")

    @staticmethod
    def remove_inventory(inventory_name: str, location: str):

        query = """
        DELETE FROM inventory
        WHERE name = %s AND location = %s
        """

        values = (inventory_name, location)

        with get_cursor() as cursor:

            cursor.execute(query, values)

            if cursor.rowcount == 0:
                logger.error(
                    f"Remove failed | Inventory not found | "
                    f"Name: {inventory_name}, Location: {location}"
                )

                raise InventoryNotFoundException(inventory_name)

            logger.info(
                f"Inventory removed | "
                f"Name: {inventory_name}, Location: {location}"
            )

    @staticmethod
    def get_inventory(inventory_name: str, location: str):
        query = """
        SELECT id, name, location FROM inventory WHERE name = %s AND location = %s
        """

        values = (inventory_name, location)

        with get_cursor() as cursor:
            cursor.execute(query, values)
            inventory_data = cursor.fetchone()

            if inventory_data is None:
                logger.error(
                    f"Fetch failed | Inventory not found | Name: {inventory_name}, Location: {location}"
                )
                raise InventoryNotFoundException(inventory_name)

            logger.debug(
                f"Inventory fetched | Name: {inventory_name}, Location: {location}"
            )

            return inventory_data

    @staticmethod
    def list_inventories():
        query = """
            SELECT id, name, location
            FROM inventory
            """
        try:
            with get_cursor() as cursor:
                cursor.execute(query)
                all_inventories = cursor.fetchall()
                logger.info("Inventories fetched successfully")
                return all_inventories
        except Exception as e:
            logger.error(
                f"Failed to fetch inventories | Error: {str(e)}"
            )
            raise

    @staticmethod
    def get_total_stock(product_name: str):
        query = """
        SELECT SUM(s.quantity) AS total_stock
        FROM inventory_stock s
        JOIN product p ON p.id = s.product_id
        WHERE p.name = %s
        """

        with get_cursor() as cursor:
            cursor.execute(query, (product_name,))
            total_stock = cursor.fetchone()[0]

        return total_stock

    def fulfill_order(self, product_name: str, required_quantity: int):
        logger.info(
            f"Order request | Product: {product_name}, Quantity: {required_quantity}"
        )
        remaining = required_quantity
        total_available = self.get_total_stock(product_name)

        if total_available < required_quantity:
            logger.warning(
                f"Order failed | Product: {product_name}, Required: {required_quantity}, Available: {total_available}"
            )
            raise InsufficientStockException(product_name, required_quantity, total_available)

        for inventory in self.inventories.values():
            if remaining <= 0:
                break

            reserved = inventory.reserve_stock(product_name, remaining)
            if reserved > 0:
                logger.info(
                    f"Stock reserved | Inventory: {inventory.name}, "
                    f"Product: {product_name}, Reserved: {reserved}"
                )
            remaining -= reserved

        logger.info(
            f"Order fulfilled | Product: {product_name}, Quantity: {required_quantity}"
        )
        print(f"Order fulfilled for '{product_name}' with quantity {required_quantity}")

    @staticmethod
    def transfer_stock(
            product_name: str,
            quantity: int,
            source_inventory_id: int,
            target_inventory_id: int
    ):

        get_product_query = """
        SELECT id
        FROM product
        WHERE name = %s
        """

        check_source_stock_query = """
        SELECT quantity
        FROM inventory_stock
        WHERE inventory_id = %s
          AND product_id = %s
        """

        reduce_source_stock_query = """
        UPDATE inventory_stock
        SET quantity = quantity - %s
        WHERE inventory_id = %s
          AND product_id = %s
        """

        check_target_stock_query = """
        SELECT quantity
        FROM inventory_stock
        WHERE inventory_id = %s
          AND product_id = %s
        """

        update_target_stock_query = """
        UPDATE inventory_stock
        SET quantity = quantity + %s
        WHERE inventory_id = %s
          AND product_id = %s
        """

        insert_target_stock_query = """
        INSERT INTO inventory_stock
        (inventory_id, product_id, quantity)
        VALUES (%s, %s, %s)
        """

        try:

            if quantity <= 0:
                raise ValueError(
                    "Transfer quantity must be greater than 0"
                )

            if source_inventory_id == target_inventory_id:
                raise ValueError(
                    "Source and target inventory cannot be same"
                )

            with get_cursor() as cursor:

                # Get product ID
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

                # Check source stock
                value = (source_inventory_id, product_id)
                cursor.execute(check_source_stock_query, value)

                source_stock = cursor.fetchone()

                if source_stock is None:
                    raise ValueError(
                        "Product not found in source inventory"
                    )

                available_quantity = source_stock[0]

                if available_quantity < quantity:
                    raise ValueError(
                        f"Insufficient stock | "
                        f"Available: {available_quantity}, "
                        f"Required: {quantity}"
                    )

                # Reduce source stock
                value = (quantity, source_inventory_id, product_id)
                cursor.execute(reduce_source_stock_query, value)

                # Check target inventory stock
                value = (target_inventory_id, product_id)

                cursor.execute(check_target_stock_query, value)

                target_stock = cursor.fetchone()

                # If exists -> update
                if target_stock:

                    value = (quantity, target_inventory_id, product_id)

                    cursor.execute(update_target_stock_query, value)

                # Else -> insert
                else:

                    value = (target_inventory_id, product_id, quantity)
                    cursor.execute(insert_target_stock_query, value)

                logger.info(
                    f"Stock transferred successfully | "
                    f"Product: {product_name} | "
                    f"Quantity: {quantity} | "
                    f"From Inventory: {source_inventory_id} | "
                    f"To Inventory: {target_inventory_id}"
                )

        except Exception as e:

            logger.exception(
                f"Failed to transfer stock | Error: {str(e)}"
            )

            raise


# inventory2 = InventoryManager.get_inventory("Zepto", "Bopal")
# print(inventory2)
# im = InventoryManager()
# print(im.get_total_stock('Milk'))
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

    def get_total_stock(self, product_name: str):
        #
        # query = """
        # select count(*) from inventory_stock is
        # join product p on p.id = is.product_id
        # where p.name = %s
        # """
        # with get_cursor() as cursor:
        #
        total = 0

        logger.debug(f"Calculating total stock | Product: {product_name}")

        for inventory in self.inventories.values():
            try:
                product = inventory.get_product(product_name)
                total += product.quantity
            except ProductNotFoundException:
                continue
        logger.info(f"Total stock | Product: {product_name}, Total: {total}")
        return total

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

    def transfer_stock(self, product_name: str, quantity: int, source_inventory: str, source_location: str, target_inventory: str, target_location: str):
        logger.info(
            f"Transfer request | Product: {product_name}, Quantity: {quantity}, "
            f"From: ({source_inventory}, {source_location}) "
            f"To: ({target_inventory}, {target_location})"
        )

        source = self.get_inventory(source_inventory, source_location)
        target = self.get_inventory(target_inventory, target_location)

        reserved = source.reserve_stock(product_name, quantity)

        if reserved == 0:
            logger.error(
                f"Transfer failed | No stock available | Product: {product_name}, Requested: {quantity}"
            )
            raise InsufficientStockException(product_name, quantity, 0)

        target.update_stock(product_name, reserved)

        logger.info(
            f"Stock transferred | Product: {product_name}, Quantity: {reserved}, "
            f"From: ({source_inventory}, {source_location}) "
            f"To: ({target_inventory}, {target_location})"
        )

        print(f"Transferred {reserved} of '{product_name}' from {source_inventory} to {target_inventory}")


# inventory2 = InventoryManager.get_inventory("Zepto", "Bopal")
# print(inventory2)
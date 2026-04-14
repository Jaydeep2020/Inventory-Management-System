from datetime import datetime

class Transaction:
    def __init__(self, product_id, inventory_name, t_type, quantity):
        self.product_id = product_id
        self.inventory_name = inventory_name
        self.type = t_type
        self.quantity = quantity
        self.timestamp = datetime.now()

    def __str__(self):
        return f"{self.type} | Product:{self.product_id} | Qty:{self.quantity} | Inv:{self.inventory_name} | Time:{self.timestamp}"
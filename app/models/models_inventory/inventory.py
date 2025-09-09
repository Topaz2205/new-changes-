from datetime import datetime

class Inventory:
    _inventories = {}  # מילון סטטי לכל המלאים לפי product_id

    def __init__(self, product_id, quantity, last_updated=None):
        self.product_id = product_id
        self.quantity = quantity  # שם תואם ל-DB

        if isinstance(last_updated, str):
            try:
                self.last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                self.last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
        else:
            self.last_updated = last_updated or datetime.now()

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,  # שם תואם ל-DB
            "last_updated": self.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
        }

# app/models/inventory_history.py

from datetime import datetime

class InventoryHistory:
    _entries = []

    def __init__(self, history_id, product_id, change_date, change_type, quantity, notes=""):
        self.history_id = history_id
        self.product_id = product_id
        self.change_date = change_date
        self.change_type = change_type  # למשל: "ADD" / "REMOVE"
        self.quantity = quantity
        self.notes = notes

    def to_dict(self):
        return self.__dict__

  
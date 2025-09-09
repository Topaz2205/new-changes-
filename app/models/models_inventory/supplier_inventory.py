# app/models/supplier_inventory.py

from datetime import datetime

class SupplierInventory:
    def __init__(self, record_id, product_id, supplier_id, quantity, unit_price, last_updated=None):
        self.record_id = record_id
        self.product_id = product_id
        self.supplier_id = supplier_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.last_updated = last_updated or datetime.now()

    def to_dict(self):
        return self.__dict__

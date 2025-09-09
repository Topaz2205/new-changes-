# app/models/warehouse_manager.py

from app.models.models_access.employee import Employee


class WarehouseManager(Employee):
    def update_inventory(self, inventory, product_id, qty):
        """
        Updates inventory quantity for a specific product.
        Assumes inventory is an Inventory class instance (e.g., inventory.py)
        """
        inventory.adjust_stock(product_id, qty)

    def view_stock_levels(self, inventory):
        """
        Returns a dictionary of current stock levels.
        Assumes inventory is an Inventory class instance.
        """
        return inventory.get_all_stock()

from app.controllers.inventory.product_controller import ProductController
from app.controllers.inventory.inventory_controller import InventoryController
from app.controllers.inventory.employee_controller import EmployeeController
from app.controllers.inventory.category_controller import CategoryController
from app.controllers.inventory.supplier_controller import SupplierController
from app.controllers.inventory.product_color_controller import ProductColorController
from app.controllers.inventory.inventory_history_controller import InventoryHistoryController
from app.controllers.inventory.supplier_inventory_controller import SupplierInventoryController  # ← חדש
from app.models.models_inventory.product import Product
from app.models.models_access.user import User  # עבור בדיקת הרשאות

class InventoryService:
    def __init__(self):
        self.product_controller = ProductController()
        self.inventory_controller = InventoryController()
        self.employee_controller = EmployeeController()
        self.category_controller = CategoryController()
        self.supplier_controller = SupplierController()
        self.color_controller = ProductColorController()
        self.history_controller = InventoryHistoryController()
        self.supplier_inventory_controller = SupplierInventoryController()  # ← חדש

    # ----------------------------------------
    # הרשאות – בדיקה לפי תפקיד (role)
    # ----------------------------------------
    def _check_permission(self, user: User, allowed_roles):
        if user.role not in allowed_roles:
            raise PermissionError(f"{user.role} is not authorized for this action")

    # -------------------------
    # פעולות על מוצרים ומלאי
    # -------------------------
    def add_new_product_with_stock(self, product: Product, initial_quantity: int):
        self.product_controller.create_product(product)
        self.inventory_controller.create_inventory(product.product_id, initial_quantity)
        self.history_controller.create_history_entry(product.product_id, initial_quantity, "מלאי התחלתי")

    def adjust_product_stock(self, product_id, amount, user: User):
        self._check_permission(user, ["Warehouse Manager"])
        self.inventory_controller.adjust_stock(product_id, amount)
        self.history_controller.create_history_entry(product_id, amount, "עדכון מלאי")

    def remove_product_stock(self, product_id, amount, user: User):
        self._check_permission(user, ["Warehouse Manager"])
        self.inventory_controller.remove_stock(product_id, amount)
        self.history_controller.create_history_entry(product_id, -amount, "הפחתת מלאי")

    def update_product_stock(self, product_id, new_quantity, user: User):
        self._check_permission(user, ["Inventory Admin", "Warehouse Manager"])
        self.inventory_controller.update_product_stock(product_id, new_quantity)
        self.history_controller.create_history_entry(product_id, new_quantity, "עדכון ישיר של מלאי")

    def list_inventory(self):
        return self.inventory_controller.get_all_stock()

    def get_full_product_data(self, product_id):
        product = self.product_controller.get_product(product_id)
        inventory = self.inventory_controller.get_stock_level(product_id)
        return {
            "product": product,
            "inventory": inventory
        }

    def discontinue_product(self, product_id):
        self.product_controller.update_product(product_id, {"discontinued": True})

    # -------------------------
    # פעולות על עובדים
    # -------------------------
    def create_employee(self, employee_data):
        self.employee_controller.create_employee(employee_data)

    def list_employees(self):
        return self.employee_controller.get_all_employees()

    def get_employee(self, employee_id):
        return self.employee_controller.get_employee_by_id(employee_id)

    def update_employee(self, employee_id, updated_data):
        self.employee_controller.update_employee(employee_id, updated_data)

    def delete_employee(self, employee_id):
        self.employee_controller.delete_employee(employee_id)

    # -------------------------
    # פעולות על קטגוריות
    # -------------------------
    def create_category(self, name, description=""):
        self.category_controller.create_category(name, description)

    def update_category(self, category_id, fields):
        self.category_controller.update_category(category_id, fields)

    def delete_category(self, category_id):
        self.category_controller.delete_category(category_id)

    def get_category(self, category_id):
        return self.category_controller.get_category(category_id)

    def list_categories(self):
        return self.category_controller.get_all_categories()

    # -------------------------
    # פעולות על ספקים
    # -------------------------
    def create_supplier(self, supplier_data, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        return self.supplier_controller.create_supplier(supplier_data)

    def update_supplier(self, supplier_id, supplier_data, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        return self.supplier_controller.update_supplier(supplier_id, supplier_data)

    def delete_supplier(self, supplier_id, user: User):
        self._check_permission(user, ["Warehouse Manager"])
        return self.supplier_controller.delete_supplier(supplier_id)

    def list_suppliers(self):
        return self.supplier_controller.get_all_suppliers()

    def get_supplier(self, supplier_id):
        return self.supplier_controller.get_supplier_by_id(supplier_id)

    # -------------------------
    # פעולות על צבעי מוצר
    # -------------------------
    def add_product_color(self, product_id, color_name, hex_code, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        return self.color_controller.create_color(product_id, color_name, hex_code)

    def get_product_colors(self, product_id):
        return self.color_controller.get_colors_by_product_id(product_id)

    def update_product_color(self, color_id, fields, user: User):
        self._check_permission(user, ["Inventory Admin"])
        return self.color_controller.update_color(color_id, fields)

    def delete_product_color(self, color_id, user: User):
        self._check_permission(user, ["Inventory Admin"])
        return self.color_controller.delete_color(color_id)

    # -------------------------
    # פעולות על היסטוריית מלאי
    # -------------------------
    def add_inventory_history(self, product_id, change, note, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        self.history_controller.create_history_entry(product_id, change, note)

    def get_inventory_history(self, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin", "Admin"])
        return self.history_controller.get_all_entries()

    def get_inventory_history_by_product(self, product_id, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin", "Admin"])
        return self.history_controller.get_entries_by_product_id(product_id)

    # -------------------------
    # פעולות על מלאי ספקים (SupplierInventory)
    # -------------------------
    def create_supplier_inventory(self, product_id, supplier_id, quantity, unit_price, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        self.supplier_inventory_controller.create_record(product_id, supplier_id, quantity, unit_price)

    def get_supplier_inventory(self, product_id, supplier_id, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin", "Admin"])
        return self.supplier_inventory_controller.get_record(product_id, supplier_id)

    def get_all_supplier_inventory(self, user: User):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin", "Admin"])
        return self.supplier_inventory_controller.get_all_records()

    def update_supplier_inventory(self, product_id, supplier_id, user: User, quantity=None, unit_price=None):
        self._check_permission(user, ["Warehouse Manager", "Inventory Admin"])
        self.supplier_inventory_controller.update_record(product_id, supplier_id, quantity, unit_price)

    def delete_supplier_inventory(self, product_id, supplier_id, user: User):
        self._check_permission(user, ["Warehouse Manager"])
        self.supplier_inventory_controller.delete_record(product_id, supplier_id)

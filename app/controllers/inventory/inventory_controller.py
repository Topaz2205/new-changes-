
from app.DB.db import get_db_connection
from app.models.models_inventory.inventory import Inventory
from datetime import datetime

class InventoryController:
    def __init__(self):
        pass

    def create_inventory(self, product_id, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Inventory (product_id, quantity, last_updated)
            VALUES (?, ?, ?)
        """, (product_id, quantity, datetime.now()))
        conn.commit()
        conn.close()
        return Inventory(product_id, quantity, datetime.now())

    def add_stock(self, product_id, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Inventory
            SET quantity = quantity + ?, last_updated = ?
            WHERE product_id = ?
        """, (amount, datetime.now(), product_id))
        conn.commit()
        conn.close()

    def remove_stock(self, product_id, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Inventory
            SET quantity = quantity - ?, last_updated = ?
            WHERE product_id = ?
        """, (amount, datetime.now(), product_id))
        conn.commit()
        conn.close()

    def get_stock_level(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Inventory WHERE product_id = ?
        """, (product_id,))
        row = cursor.fetchone()
        conn.close()
        return Inventory(**dict(row)) if row else None

    from datetime import datetime
    from app.DB.db import get_db_connection

    def get_all_stock(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                Inventory.product_id,
                Products.name AS product_name,
                Categories.name AS category_name,
                ProductColors.color_name AS color_name,
                Suppliers.company_name AS supplier_name,
                Inventory.quantity,
                Inventory.last_updated
            FROM Inventory
            JOIN Products ON Inventory.product_id = Products.id
            LEFT JOIN Categories ON Products.category_id = Categories.id
            LEFT JOIN ProductColors ON Products.color_id = ProductColors.id
            LEFT JOIN Suppliers ON Products.supplier_id = Suppliers.id
        """)

        rows = cursor.fetchall()
        conn.close()

        inventory_list = []
        for row in rows:
            # צור אובייקט Inventory עם נתוני מלאי
            inv = Inventory(
                product_id=row["product_id"],
                quantity=row["quantity"],
                last_updated=row["last_updated"]
            )

            # הפוך את האובייקט למילון
            inv_dict = inv.to_dict()

            # הוסף את שדות המידע הנוספים מהמוצר
            inv_dict["product_name"] = row["product_name"]
            inv_dict["category_name"] = row["category_name"]
            inv_dict["color_name"] = row["color_name"]
            inv_dict["supplier_name"] = row["supplier_name"]

            inventory_list.append(inv_dict)

        return inventory_list



    def update_product_stock(self, product_id, new_quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Inventory
            SET quantity = ?, last_updated = ?
            WHERE product_id = ?
        """, (new_quantity, datetime.now(), product_id))
        conn.commit()
        conn.close()

    

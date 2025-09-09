# app/controllers/inventory/supplier_inventory_controller.py

from datetime import datetime
from app.DB.db import get_db_connection
from app.models.models_inventory.supplier_inventory import SupplierInventory

class SupplierInventoryController:
    def __init__(self):
        pass

    # יצירת רשומה חדשה
    def create_record(self, product_id, supplier_id, quantity, unit_price):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO SupplierInventory (product_id, supplier_id, quantity, unit_price, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (product_id, supplier_id, quantity, unit_price, datetime.now()))

        conn.commit()
        conn.close()

    # שליפה של רשומה מסוימת לפי product_id + supplier_id
    def get_record(self, product_id, supplier_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM SupplierInventory
            WHERE product_id = ? AND supplier_id = ?
        """, (product_id, supplier_id))

        row = cursor.fetchone()
        conn.close()

        if row:
            return SupplierInventory(*row).to_dict()
        return None

    # שליפה של כל הרשומות
    def get_all_records(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM SupplierInventory")
        rows = cursor.fetchall()
        conn.close()

        return [SupplierInventory(*row).to_dict() for row in rows]

    # עדכון כמות או מחיר עבור ספק+מוצר
    def update_record(self, product_id, supplier_id, quantity=None, unit_price=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        # בניית עדכון דינמי
        fields = []
        values = []

        if quantity is not None:
            fields.append("quantity = ?")
            values.append(quantity)

        if unit_price is not None:
            fields.append("unit_price = ?")
            values.append(unit_price)

        fields.append("last_updated = ?")
        values.append(datetime.now())

        values.extend([product_id, supplier_id])

        sql = f"""
            UPDATE SupplierInventory
            SET {', '.join(fields)}
            WHERE product_id = ? AND supplier_id = ?
        """

        cursor.execute(sql, tuple(values))
        conn.commit()
        conn.close()

    # מחיקת רשומה
    def delete_record(self, product_id, supplier_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM SupplierInventory
            WHERE product_id = ? AND supplier_id = ?
        """, (product_id, supplier_id))

        conn.commit()
        conn.close()

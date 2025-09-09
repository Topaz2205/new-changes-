# app/controllers/inventory/inventory_history_controller.py

from app.DB.db import get_db_connection
from app.models.models_inventory.inventory_history import InventoryHistory

class InventoryHistoryController:
    def __init__(self):
        pass

    # יצירת רשומת היסטוריה חדשה
    def create_history_entry(self, product_id, change, note=""):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO InventoryHistory (product_id, change, note)
            VALUES (?, ?, ?)
        """, (product_id, change, note))

        conn.commit()
        conn.close()

    # שליפת כל רשומות ההיסטוריה
    def get_all_entries(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM InventoryHistory ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        return [InventoryHistory(*row).to_dict() for row in rows]

    # שליפת היסטוריה לפי מזהה מוצר
    def get_entries_by_product_id(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM InventoryHistory
            WHERE product_id = ?
            ORDER BY timestamp DESC
        """, (product_id,))
        rows = cursor.fetchall()
        conn.close()

        return [InventoryHistory(*row).to_dict() for row in rows]

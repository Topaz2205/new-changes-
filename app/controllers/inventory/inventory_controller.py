from datetime import datetime
from app.DB.db import get_db_connection
from app.models.models_inventory.inventory import Inventory


class InventoryController:
    def __init__(self):
        pass

    # --- עזר פנימי: יוצר שורת מלאי אם לא קיימת ---
    def _ensure_inventory_row(self, cursor, product_id: int):
        cursor.execute("SELECT product_id FROM Inventory WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        if not row:
            now = datetime.now()
            cursor.execute(
                "INSERT INTO Inventory (product_id, quantity, last_updated) VALUES (?, ?, ?)",
                (product_id, 0, now),
            )

    # --- יצירת שורת מלאי מפורשת (אם תרצה להשתמש בה) ---
    def create_inventory(self, product_id, quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Inventory (product_id, quantity, last_updated) VALUES (?, ?, ?)",
            (product_id, quantity, datetime.now()),
        )
        conn.commit()
        conn.close()
        return Inventory(product_id, quantity, datetime.now())

    # --- הוספת מלאי ---
    def add_stock(self, product_id, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        self._ensure_inventory_row(cursor, product_id)
        cursor.execute(
            "UPDATE Inventory SET quantity = quantity + ?, last_updated = ? WHERE product_id = ?",
            (amount, datetime.now(), product_id),
        )
        conn.commit()
        conn.close()

    # --- הורדת מלאי ---
    def remove_stock(self, product_id, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        self._ensure_inventory_row(cursor, product_id)
        cursor.execute(
            "UPDATE Inventory SET quantity = quantity - ?, last_updated = ? WHERE product_id = ?",
            (amount, datetime.now(), product_id),
        )
        conn.commit()
        conn.close()

    # --- קריאת רמת מלאי למוצר בודד ---
    def get_stock_level(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, quantity, last_updated FROM Inventory WHERE product_id = ?", (product_id,))
        row = cursor.fetchone()
        conn.close()
        return Inventory(**dict(row)) if row else None

    # --- רשימת מלאי כוללת: מחזיר *את כל המוצרים* גם אם אין להם רשומת מלאי (כמות=0) ---
    def get_all_stock(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.id                           AS product_id,
                p.name                         AS product_name,
                COALESCE(c.name, '')           AS category_name,
                COALESCE(col.color_name, '')   AS color_name,
                COALESCE(col.hex_code, '')   AS color_hex,
                p.image_url                    AS image_url,
                COALESCE(s.company_name, '')   AS supplier_name,
                COALESCE(i.quantity, p.units_in_stock, 0)        AS quantity,
                i.last_updated                 AS last_updated
            FROM Products p
            LEFT JOIN Categories     c   ON c.id  = p.category_id
            LEFT JOIN ProductColors  col ON col.id = p.color_id
            LEFT JOIN Suppliers      s   ON s.id  = p.supplier_id
            LEFT JOIN Inventory      i   ON i.product_id = p.id     -- <<< זה החלק הקריטי
            ORDER BY p.id
        """)

        rows = cursor.fetchall()
        conn.close()

        # מחזירים מילונים נוחים לתבנית
        inventory_list = []
        for row in rows:
            inventory_list.append({
                "product_id":     row["product_id"],
                "product_name":   row["product_name"],
                "category_name":  row["category_name"],
                "color_name":     row["color_name"],
                "color_hex":      row["color_hex"], 
                "image_url":    row["image_url"],
                "supplier_name":  row["supplier_name"],
                "quantity":       row["quantity"],          # 0 אם אין רשומת מלאי
                "last_updated":   row["last_updated"],      # יכול להיות None אם אין רשומה
            })
        return inventory_list

    # --- עדכון כמות ישירה ---
    def update_product_stock(self, product_id, new_quantity):
        conn = get_db_connection()
        cursor = conn.cursor()
        self._ensure_inventory_row(cursor, product_id)
        cursor.execute(
            "UPDATE Inventory SET quantity = ?, last_updated = ? WHERE product_id = ?",
            (new_quantity, datetime.now(), product_id),
        )
        conn.commit()
        conn.close()

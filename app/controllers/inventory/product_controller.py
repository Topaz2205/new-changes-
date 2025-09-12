# app/controllers/inventory/product_controller.py

from app.DB.db import get_db_connection
from app.models.models_inventory.product import Product
from datetime import datetime

class ProductController:
    def __init__(self):
        pass

    def create_product(self, data):
        """
        מקבל dict או אובייקט Product ומכניס שורה ל-Products.
        - ממיר discontinued ל-True/False
        - ממיר price ל-float ומזהים ל-int
        - מאפס לשדות NULL מותרים כשנשלח ריק
        - מוסיף created_at/updated_at = CURRENT_TIMESTAMP
        """

        # מיפוי קלט -> עמודות DB (לפי שמות השדות אצלך)
        mapping = {
            'name'             : 'name',
            'supplier_id'      : 'supplier_id',
            'category_id'      : 'category_id',
            'quantity_per_unit': 'quantity_per_unit',
            'color_id'         : 'color_id',
            'price'            : 'price',
            'unit_price'       : 'price',   # תאימות: unit_price -> price
            'units_in_stock'   : 'units_in_stock',
            'description'      : 'description',
            'image_url'        : 'image_url',
            'discontinued'     : 'discontinued',
        }
        nullable_cols = {'color_id', 'image_url', 'quantity_per_unit', 'description'}

        # --- נרמול קלט לאובייקט dict ---
        def _coerce_to_dict(obj):
            if isinstance(obj, dict):
                return obj
            if hasattr(obj, 'to_dict'):
                return obj.to_dict()
            # נפילה לאטריבוטים לפי שמות המפתחות המוכרים
            out = {}
            for k in mapping.keys():
                if hasattr(obj, k):
                    out[k] = getattr(obj, k)
            return out

        data = _coerce_to_dict(data) or {}

        # עזרי טיפוס
        def _is_empty(v):
            return v is None or (isinstance(v, str) and v.strip() == "")

        def _to_bool(v):
            if isinstance(v, bool):
                return v
            s = str(v).strip().lower() if v is not None else ""
            if s in ("1", "true", "t", "yes", "y", "on"):
                return True
            if s in ("0", "false", "f", "no", "n", "off", ""):
                return False
            return False  # ברירת מחדל בטוחה

        cols, vals, placeholders = [], [], []

        # שמירה על סדר יציב לפי mapping
        for key, col in mapping.items():
            if key not in data:
                continue
            val = data.get(key)

            # נרמול BOOLEAN
            if key == 'discontinued':
                val = _to_bool(val)

            # NULL לשדות ריקים מותרים
            if key in nullable_cols and _is_empty(val):
                cols.append(col); vals.append(None); placeholders.append("?")
                continue

            # המרות טיפוס
            try:
                if col == 'price' and not _is_empty(val):
                    val = float(val)
                elif key in ('supplier_id', 'category_id', 'units_in_stock', 'color_id') and not _is_empty(val):
                    val = int(val)
            except (TypeError, ValueError):
                # ערך לא תקין – מדלגים על השדה
                continue

            cols.append(col); vals.append(None if _is_empty(val) else val); placeholders.append("?")

        # אם לא סופק discontinued – שים False כברירת מחדל
        if 'discontinued' not in data:
            cols.append('discontinued'); vals.append(False); placeholders.append("?")

        # חותמות זמן מה-DB (ללא פרמטרים)
        cols.extend(['created_at', 'updated_at'])
        placeholders.extend(['CURRENT_TIMESTAMP', 'CURRENT_TIMESTAMP'])

        sql = f"INSERT INTO Products ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, tuple(vals))
        conn.commit()
        conn.close()

    def get_product(self, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                Products.id AS id,
                Products.name,
                Suppliers.company_name AS supplier,
                Categories.name AS category,
                Products.quantity_per_unit,
                Products.units_in_stock,
                ProductColors.color_name AS color_name,
                ProductColors.hex_code,
                Products.description,
                Products.image_url,
                Products.price AS unit_price,
                Products.discontinued
            FROM Products
            LEFT JOIN Suppliers ON Products.supplier_id = Suppliers.id
            LEFT JOIN Categories ON Products.category_id = Categories.id
            LEFT JOIN ProductColors ON Products.color_id = ProductColors.id
            WHERE Products.id = ?
        """, (id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None



    def update_product(self, product_id: int, updates: dict):
        """
        עדכון חלקי של מוצר:
        - מעדכן רק מפתחות שמופיעים ב-updates
        - מיפוי unit_price -> price
        - המרת טיפוסים בטוחה (int/float/bool)
        - תמיכה באיפוס שדות ניתנים ל-NULL
        - updated_at מתעדכן אוטומטית (DB CURRENT_TIMESTAMP)
        """

        if not updates:
            return

        # מיפוי מפתחות מהקוד לעמודות DB
        mapping = {
            'name'             : 'name',
            'supplier_id'      : 'supplier_id',
            'category_id'      : 'category_id',
            'quantity_per_unit': 'quantity_per_unit',
            'color_id'         : 'color_id',
            'price'            : 'price',
            'unit_price'       : 'price',          # תאימות: unit_price -> price
            'units_in_stock'   : 'units_in_stock',
            'description'      : 'description',
            'image_url'        : 'image_url',
            'discontinued'     : 'discontinued',
        }

        # אילו *מפתחות* מותר לאפס ל-NULL
        nullable_cols = {'color_id', 'image_url', 'quantity_per_unit', 'description'}

        def _to_bool(v):
            if isinstance(v, bool):
                return v
            s = str(v).strip().lower() if v is not None else ''
            if s in ('1', 'true', 't', 'yes', 'y', 'on'):
                return True
            if s in ('0', 'false', 'f', 'no', 'n', 'off', ''):
                return False
            return None  # ערך לא ברור – עדיף לא לעדכן

        set_parts, params = [], []

        for key, value in (updates or {}).items():
            if key not in mapping:
                continue

            col = mapping[key]

            # נרמול בוליאני→True/False (לא 0/1)
            if key == 'discontinued':
                value = _to_bool(value)
                if value is None:
                    # לא לעדכן את העמודה אם הערך לא ברור
                    continue

            # איפוס שדות ניתנים ל-NULL
            if key in nullable_cols and (value is None or value == ''):
                set_parts.append(f"{col} = NULL")
                continue

            # המרת טיפוסים
            try:
                if col == 'price' and value not in (None, ''):
                    value = float(value)
                elif key in ('supplier_id', 'category_id', 'units_in_stock', 'color_id') and value not in (None, ''):
                    value = int(value)
            except (TypeError, ValueError):
                # טיפוס לא תקין – דלג על המפתח הזה
                continue

            if value is None:
                # אל תדרוס עמודות לא-ניתנות ל-NULL
                continue

            set_parts.append(f"{col} = ?")
            params.append(value)

        if not set_parts:
            return

        # חותמת זמן מה-DB (ללא פרמטר)
        set_parts.append("updated_at = CURRENT_TIMESTAMP")

        sql = f"UPDATE Products SET {', '.join(set_parts)} WHERE id = ?"
        params.append(product_id)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        conn.close()




    def delete_product(self, product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()

    def adjust_stock(self, product_id, amount):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Products
            SET units_in_stock = units_in_stock + ?, updated_at = ?
            WHERE id = ?
        """, (amount, datetime.now(), product_id))
        conn.commit()
        conn.close()

    def get_all_products(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.id                                   AS id,
                p.name                                 AS name,

                COALESCE(s.company_name, '')           AS supplier_name,
                COALESCE(c.name, '')                   AS category_name,

                /* הכמות: קודם Inventory ואז Products.units_in_stock */
                COALESCE(i.quantity, p.units_in_stock, 0) AS stock,

                p.price                                AS price,
                p.price                                AS unit_price,  -- תאימות תבניות

                p.quantity_per_unit,
                col.color_name                         AS color_name,
                col.hex_code                           AS hex_code,
                p.description,
                p.image_url,
                p.discontinued,

                /* תאימות לשמות ישנים אם קיימים בתבניות */
                COALESCE(i.quantity, p.units_in_stock, 0) AS units_in_stock,
                COALESCE(s.company_name, '')           AS supplier,
                COALESCE(c.name, '')                   AS category

            FROM Products p
            LEFT JOIN Suppliers     s   ON s.id  = p.supplier_id
            LEFT JOIN Categories    c   ON c.id  = p.category_id
            LEFT JOIN ProductColors col ON col.id = p.color_id
            LEFT JOIN Inventory     i   ON i.product_id = p.id
            ORDER BY p.id
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]




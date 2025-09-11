# app/controllers/inventory/product_controller.py

from app.DB.db import get_db_connection
from app.models.models_inventory.product import Product
from datetime import datetime

class ProductController:
    def __init__(self):
        pass

    def create_product(self, product):
        conn = get_db_connection()
        cur = conn.cursor()

        # תמיכה גם אם במקרה יגיע product.price (לא רק unit_price)
        unit_price = getattr(product, "unit_price", None)
        if unit_price is None:
            unit_price = getattr(product, "price", 0)

        now = datetime.now()
        discontinued = int(bool(getattr(product, "discontinued", 0)))

        cur.execute("""
            INSERT INTO Products (
                name, supplier_id, category_id, description,
                price, image_url, units_in_stock, quantity_per_unit,
                color_id, discontinued, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product.name,
            product.supplier_id,
            product.category_id,
            product.description or "",
            float(unit_price),
            product.image_url or "",
            int(product.units_in_stock or 0),
            product.quantity_per_unit or "",
            product.color_id if getattr(product, "color_id", None) not in ("", None) else None,
            discontinued,
            getattr(product, "created_at", None) or now,
            getattr(product, "updated_at", None) or now,
        ))
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
        - נעדכן רק את המפתחות שמופיעים ב-updates.
        - מיפוי unit_price → price (DB).
        - המרת טיפוסים בטוחה (int/float/bool).
        - תמיכה באיפוס שדות ניתנים ל-NULL (למשל color_id, image_url).
        - עדכון updated_at אוטומטית.
        """
        if not updates:
            return

        conn = get_db_connection()
        cur = conn.cursor()  

        # מיפוי מפתחות מהקוד לעמודות בטבלה
        mapping = {
            'name'             : 'name',
            'supplier_id'      : 'supplier_id',
            'category_id'      : 'category_id',
            'quantity_per_unit': 'quantity_per_unit',
            'color_id'         : 'color_id',
            'price'            : 'price',     # עמודה אמיתית ב-DB
            'unit_price'       : 'price',     # תאימות: אם שולחים unit_price נמפה ל-price
            'units_in_stock'   : 'units_in_stock',
            'description'      : 'description',
            'image_url'        : 'image_url',
            'discontinued'     : 'discontinued',
        }

        # אילו עמודות מותר לאפס ל-NULL במפורש (כשהערך None/"" מהטופס)
        nullable_cols = {'color_id', 'image_url', 'quantity_per_unit', 'description'}

        set_parts, params = [], []

        for key, value in (updates or {}).items():
            if key not in mapping:
                continue

            col = mapping[key]

            # נרמול בוליאני
            if key == 'discontinued':
                value = 1 if value in (True, 1, '1', 'true', 'on', 'yes') else 0

            # איפוס שדות ניתנים ל-NULL
            if key in nullable_cols and (value is None or value == ''):
                set_parts.append(f"{col} = NULL")
                continue

            # המרת טיפוסים בטוחה
            try:
                if col == 'price' and value is not None and value != '':
                    value = float(value)
                elif key in ('supplier_id', 'category_id', 'units_in_stock', 'color_id') and value not in (None, ''):
                    value = int(value)
            except (TypeError, ValueError):
                # אם הטיפוס לא תקין מדלגים על המפתח הזה במקום להפיל את הבקשה כולה
                continue

            # נתעלם מ-None עבור עמודות שאינן nullable (שלא נדרוס חובה)
            if value is None:
                continue

            set_parts.append(f"{col} = ?")
            params.append(value)

        if not set_parts:
            conn.close()
            return

        # עדכון חותמת זמן
        set_parts.append("updated_at = ?")
        params.append(datetime.now())

        # WHERE
        params.append(product_id)
        sql = f"UPDATE Products SET {', '.join(set_parts)} WHERE id = ?"

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




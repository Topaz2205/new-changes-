# app/controllers/inventory/product_controller.py

from app.DB.db import get_db_connection
from app.models.models_inventory.product import Product
from datetime import datetime

class ProductController:
    def __init__(self):
        pass

    def create_product(self, product: Product):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
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
            product.description,
            product.unit_price,
            product.image_url,
            product.units_in_stock,
            product.quantity_per_unit,
            product.color_id,
            product.discontinued,
            product.created_at or datetime.now(),
            product.updated_at or datetime.now()
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

    def update_product(self, product_id, updates: dict):
        conn = get_db_connection()
        cursor = conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values())
        values.append(datetime.now())  # updated_at
        values.append(product_id)
        cursor.execute(f"""
            UPDATE Products
            SET {set_clause}, updated_at = ?
            WHERE id = ?
        """, values)
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
                Products.id AS id,
                Products.name,
                Suppliers.company_name AS supplier,
                Categories.name AS category,
                Products.quantity_per_unit,
                Products.units_in_stock,
                ProductColors.color_name AS color_name,
                ProductColors.hex_code AS hex_code,
                Products.description,
                Products.image_url,
                Products.price AS unit_price,
                Products.discontinued
            FROM Products
            LEFT JOIN Suppliers ON Products.supplier_id = Suppliers.id
            LEFT JOIN Categories ON Products.category_id = Categories.id
            LEFT JOIN ProductColors ON Products.color_id = ProductColors.id
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

# app/controllers/orders/order_details_controller.py

from app.DB.db import get_db_connection
from app.models.models_orders.order_details import OrderDetail

class OrderDetailsController:
    def __init__(self):
        pass

    def add_order_detail(self, order_id, product_id, quantity, unit_price, discount):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO OrderDetails (order_id, product_id, quantity, unit_price, discount)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, product_id, quantity, unit_price, discount))

        conn.commit()
        conn.close()

    def get_details_by_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, order_id, product_id, quantity, unit_price, discount
            FROM OrderDetails
            WHERE order_id = ?
        """, (order_id,))
        
        rows = cursor.fetchall()
        conn.close()

        return [OrderDetail(*row).to_dict() for row in rows]

    def delete_order_detail(self, detail_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM OrderDetails WHERE id = ?
        """, (detail_id,))

        conn.commit()
        conn.close()

from app.DB.db import get_db_connection
from app.models.models_orders.order_update import OrderUpdate
from datetime import datetime

class OrderUpdateController:
    def __init__(self):
        pass

    def record_update(self, order_id, update_type, old_value, new_value):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now()

        cursor.execute("""
            INSERT INTO OrderUpdates (order_id, update_type, old_value, new_value, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (order_id, update_type, old_value, new_value, now))

        conn.commit()
        conn.close()

    def get_updates_by_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, order_id, update_type, old_value, new_value, updated_at
            FROM OrderUpdates
            WHERE order_id = ?
        """, (order_id,))

        rows = cursor.fetchall()
        conn.close()

        return [OrderUpdate(*row).to_dict() for row in rows]

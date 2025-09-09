from app.DB.db import get_db_connection
from app.models.models_orders.deliverystatus import DeliveryStatus
from datetime import datetime

class DeliveryStatusController:
    def __init__(self):
        pass

    def update_status(self, order_id, new_status, delay_reason=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()

        # בדיקה אם יש כבר סטטוס
        cursor.execute("SELECT status_id FROM DeliveryStatus WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()

        if row:
            # עדכון רשומה קיימת
            cursor.execute("""
                UPDATE DeliveryStatus
                SET status = ?, delay_reason = ?, updated_at = ?
                WHERE order_id = ?
            """, (new_status, delay_reason, now, order_id))
        else:
            # יצירת רשומה חדשה
            cursor.execute("""
                INSERT INTO DeliveryStatus (order_id, status, delay_reason, updated_at)
                VALUES (?, ?, ?, ?)
            """, (order_id, new_status, delay_reason, now))

        conn.commit()
        conn.close()

    def get_status_by_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT status_id, order_id, status, delay_reason, updated_at
            FROM DeliveryStatus
            WHERE order_id = ?
        """, (order_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return DeliveryStatus(*row).to_dict()
        return None

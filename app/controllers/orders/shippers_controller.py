from app.DB.db import get_db_connection
from app.models.models_orders.shippers import Shipper
from datetime import datetime

class ShipperController:
    def __init__(self):
        pass

    def register_shipper(self, company_name, phone=None):
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute("""
            INSERT INTO Shippers (company_name, phone, created_at)
            VALUES (?, ?, ?)
        """, (company_name, phone, now))

        conn.commit()
        shipper_id = cursor.lastrowid
        conn.close()

        return Shipper(shipper_id, company_name, phone, now)

    def get_all_shippers(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, company_name, phone, created_at
            FROM Shippers
        """)

        rows = cursor.fetchall()
        conn.close()

        return [Shipper(*row).to_dict() for row in rows]

    def get_shipper_by_id(self, shipper_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, company_name, phone, created_at
            FROM Shippers
            WHERE id = ?
        """, (shipper_id,))

        row = cursor.fetchone()
        conn.close()

        return Shipper(*row).to_dict() if row else None

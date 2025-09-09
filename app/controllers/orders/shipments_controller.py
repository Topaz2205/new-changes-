from app.DB.db import get_db_connection
from app.models.models_orders.shipments import Shipment
from datetime import datetime

class ShipmentController:
    def __init__(self):
        pass

    def create_shipment(self, order_id, tracking_number, shipping_provider,
                        estimated_delivery_date, status="Pending"):
        conn = get_db_connection()
        cursor = conn.cursor()

        now = datetime.now()
        cursor.execute("""
            INSERT INTO Shipments (order_id, tracking_number, shipping_provider, 
                                   shipped_date, estimated_delivery_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (order_id, tracking_number, shipping_provider, now,
              estimated_delivery_date, status))
        conn.commit()
        shipment_id = cursor.lastrowid
        conn.close()

        return self.get_shipment_by_id(shipment_id)

    def get_shipment_by_id(self, shipment_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, order_id, tracking_number, shipping_provider,
                   shipped_date, estimated_delivery_date, delivered_date, status
            FROM Shipments
            WHERE id = ?
        """, (shipment_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Shipment(*row).to_dict()
        return None

    def get_shipments_by_order(self, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, order_id, tracking_number, shipping_provider,
                   shipped_date, estimated_delivery_date, delivered_date, status
            FROM Shipments
            WHERE order_id = ?
        """, (order_id,))
        rows = cursor.fetchall()
        conn.close()
        return [Shipment(*row).to_dict() for row in rows]

    def update_status(self, shipment_id, new_status, delivered_date=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now()

        if new_status.lower() == "delivered" and delivered_date is None:
            delivered_date = now

        cursor.execute("""
            UPDATE Shipments
            SET status = ?, delivered_date = ?
            WHERE id = ?
        """, (new_status, delivered_date, shipment_id))
        conn.commit()
        conn.close()

        return self.get_shipment_by_id(shipment_id)

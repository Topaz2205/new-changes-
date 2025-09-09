from datetime import datetime

class Shipment:
    def __init__(self, id, order_id, tracking_number, shipping_provider,
                 shipped_date=None, estimated_delivery_date=None, delivered_date=None, status="Pending"):
        self.id = id
        self.order_id = order_id
        self.tracking_number = tracking_number
        self.shipping_provider = shipping_provider
        self.shipped_date = self._parse_date(shipped_date)
        self.estimated_delivery_date = self._parse_date(estimated_delivery_date)
        self.delivered_date = self._parse_date(delivered_date)
        self.status = status

    def _parse_date(self, date_val):
        if isinstance(date_val, str):
            return datetime.fromisoformat(date_val)
        return date_val or None

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
            "shipping_provider": self.shipping_provider,
            "shipped_date": self.shipped_date.isoformat() if self.shipped_date else None,
            "estimated_delivery_date": self.estimated_delivery_date.isoformat() if self.estimated_delivery_date else None,
            "delivered_date": self.delivered_date.isoformat() if self.delivered_date else None,
            "status": self.status
        }

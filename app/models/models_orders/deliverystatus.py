from datetime import datetime

class DeliveryStatus:
    def __init__(self, status_id, order_id, status, delay_reason=None, updated_at=None):
        self.status_id = status_id
        self.order_id = order_id
        self.status = status
        self.delay_reason = delay_reason
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "status_id": self.status_id,
            "order_id": self.order_id,
            "status": self.status,
            "delay_reason": self.delay_reason,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }

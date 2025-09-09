from datetime import datetime

class OrderUpdate:
    def __init__(self, update_id, order_id, update_type, old_value, new_value, updated_at=None):
        self.update_id = update_id
        self.order_id = order_id
        self.update_type = update_type
        self.old_value = old_value
        self.new_value = new_value
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "update_id": self.update_id,
            "order_id": self.order_id,
            "update_type": self.update_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "updated_at": self.updated_at.isoformat()
        }

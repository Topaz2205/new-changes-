from datetime import datetime

class Shipper:
    def __init__(self, shipper_id, company_name, phone=None, created_at=None):
        self.shipper_id = shipper_id
        self.company_name = company_name
        self.phone = phone
        self.created_at = (
            datetime.fromisoformat(created_at) if isinstance(created_at, str)
            else created_at or datetime.now()
        )

    def to_dict(self):
        return {
            "shipper_id": self.shipper_id,
            "company_name": self.company_name,
            "phone": self.phone,
            "created_at": self.created_at.isoformat()
        }

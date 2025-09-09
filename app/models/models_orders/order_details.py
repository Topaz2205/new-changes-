
from decimal import Decimal

class OrderDetail:
    def __init__(self, order_detail_id, order_id, product_id, quantity, unit_price,
                 discount, total_price):
        self.order_detail_id = order_detail_id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = Decimal(unit_price)
        self.discount = Decimal(discount)
        self.total_price = Decimal(total_price)

    def calculate_line_total(self):
        self.total_price = (self.unit_price * self.quantity) * (1 - self.discount)

    def to_dict(self):
        return {
            "order_detail_id": self.order_detail_id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "discount": float(self.discount),
            "total_price": float(self.total_price)
        }

# app/models/models_orders/order.py

from datetime import datetime

class Order:
    def __init__(self, order_id, customer_id, employee_id, user_id,
                 order_date, shipped_date, status, ship_via, freight,
                 total_amount, expected_delivery=None, actual_delivery=None,
                 updated_at=None,  # <<< הוספנו
                 customer_name=None, employee_name=None):

        self.order_id = order_id
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.user_id = user_id
        self.order_date = self._to_datetime(order_date)
        self.shipped_date = self._to_datetime(shipped_date)
        self.status = status
        self.ship_via = ship_via
        self.freight = freight
        self.total_amount = total_amount
        self.expected_delivery = self._to_datetime(expected_delivery)
        self.actual_delivery = self._to_datetime(actual_delivery)
        self.updated_at = self._to_datetime(updated_at)  # <<< חדש
        self.customer_name = customer_name
        self.employee_name = employee_name


    def _to_datetime(self, value):
        if value in (None, "", "NULL"):
            return None
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None  # או אפשר להחזיר value אם זו מחרוזת לא תאריך שאתה רוצה לשמור
        return value

    def to_dict(self):
        return self.__dict__

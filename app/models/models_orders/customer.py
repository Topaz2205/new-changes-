# app/models/models_orders/customer.py

from datetime import datetime

class Customer:
    def __init__(self, customer_id, contact_name, contact_title, address, customer_type,
                 customer_tag, city, postal_code, country, phone, email, created_at=None):
        self.customer_id = customer_id
        self.contact_name = contact_name
        self.contact_title = contact_title
        self.address = address
        self.customer_type = customer_type
        self.customer_tag = customer_tag
        self.city = city
        self.postal_code = postal_code
        self.country = country
        self.phone = phone
        self.email = email
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return self.__dict__

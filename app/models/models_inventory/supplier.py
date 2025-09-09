class Supplier:
    def __init__(self, id, company_name, contact_name, contact_email="", address="", city="", country="", phone=""):
        self.id = id
        self.company_name = company_name
        self.contact_name = contact_name
        self.contact_email = contact_email
        self.address = address
        self.city = city
        self.country = country
        self.phone = phone

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "phone": self.phone
        }

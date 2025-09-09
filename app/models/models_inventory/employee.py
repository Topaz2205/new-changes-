class Employee:
    def __init__(self, employee_id, first_name, last_name, title, birth_date,
                 hire_date, address, city, country, postal_code,
                 phone, email, manager_id=None):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.title = title
        self.birth_date = birth_date
        self.hire_date = hire_date
        self.address = address
        self.city = city
        self.country = country
        self.postal_code = postal_code
        self.phone = phone
        self.email = email
        self.manager_id = manager_id

        # לוגיקה פנימית (לא נשמרת ב־DB)
        self.manager = None
        self.subordinates = []

    def get_subordinates(self):
        return self.subordinates

    def assign_subordinate(self, employee):
        self.subordinates.append(employee)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "title": self.title,
            "birth_date": self.birth_date,
            "hire_date": self.hire_date,
            "address": self.address,
            "city": self.city,
            "country": self.country,
            "postal_code": self.postal_code,
            "phone": self.phone,
            "email": self.email,
            "manager_id": self.manager_id,
            "subordinates": [e.employee_id for e in self.subordinates]
        }

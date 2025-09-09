class Employee:
    def __init__(self, employee_id, user_id, position, manager_id=None):
        self.employee_id = employee_id
        self.user_id = user_id
        self.position = position
        self.manager_id = manager_id  # ID של המנהל (כפי שב-ERD)
        
        # תכונות אופציונליות שאינן ב־ERD, אך יכולות להישמר בזיכרון
        self.manager = None        # אובייקט Employee אחר (לא חובה)
        self.subordinates = []     # רשימת עובדים כפופים

    def get_subordinates(self):
        return self.subordinates

    def assign_subordinate(self, employee):
        self.subordinates.append(employee)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "user_id": self.user_id,
            "position": self.position,
            "manager_id": self.manager_id,
            "subordinates": [e.employee_id for e in self.subordinates]
        }

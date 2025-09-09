# app/models/category.py

class Category:

    def __init__(self, id, name, description=""):
        self.id = id
        self.name = name
        self.description = description

    def to_dict(self):
        return {
            "category_id": self.id,
            "name": self.name,
            "description": self.description
        }


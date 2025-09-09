from datetime import datetime

class Product:
    def __init__(self, id, name, supplier_id, category_id, quantity_per_unit,
                 color_id, unit_price, units_in_stock=0, description=None,
                 image_url=None, discontinued=False, created_at=None, updated_at=None):
        self.id = id
        self.name = name
        self.supplier_id = supplier_id
        self.category_id = category_id
        self.quantity_per_unit = quantity_per_unit
        self.color_id = color_id
        self.unit_price = unit_price
        self.units_in_stock = units_in_stock
        self.description = description
        self.image_url = image_url
        self.discontinued = discontinued
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "supplier_id": self.supplier_id,
            "category_id": self.category_id,
            "quantity_per_unit": self.quantity_per_unit,
            "color_id": self.color_id,
            "unit_price": self.unit_price,
            "units_in_stock": self.units_in_stock,
            "description": self.description,
            "image_url": self.image_url,
            "discontinued": self.discontinued,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

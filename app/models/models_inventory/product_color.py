# models_inventory/product_color.py
class ProductColor:
    def __init__(self, id, color_name, hex_code):
        self.id = id
        self.color_name = color_name
        self.hex_code = hex_code

    def to_dict(self):
        return {
            "id": self.id,
            "color_name": self.color_name,
            "hex_code": self.hex_code
        }

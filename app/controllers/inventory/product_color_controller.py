# controllers/inventory/color_controller.py
from app.DB.db import get_db_connection
from app.models.models_inventory.product_color import ProductColor

class ColorController:
    def get_all_colors(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ProductColors")
        rows = cursor.fetchall()
        conn.close()
        return [ProductColor(row["id"], row["color_name"], row["hex_code"]).to_dict() for row in rows]

    def get_color_by_id(self, color_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ProductColors WHERE id = ?", (color_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return ProductColor(row["id"], row["color_name"], row["hex_code"]).to_dict()
        return None

    def create_color(self, color_name, hex_code):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ProductColors (color_name, hex_code) VALUES (?, ?)", (color_name, hex_code))
        conn.commit()
        conn.close()

    def update_color(self, color_id, updated_data):
        print(">> Update function using dictionary called")
        color_name = updated_data["color_name"]
        hex_code = updated_data["hex_code"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ProductColors SET color_name = ?, hex_code = ? WHERE id = ?",
            (color_name, hex_code, color_id)
        )
        conn.commit()
        conn.close()

    def delete_color(self, color_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ProductColors WHERE id = ?", (color_id,))
        conn.commit()
        conn.close()

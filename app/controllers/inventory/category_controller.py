from app.DB.db import get_db_connection
from app.models.models_inventory.category import Category

class CategoryController:
    def __init__(self):
        pass

    def create_category(self, name, description=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Categories (name, description) VALUES (?, ?)", (name, description))
        conn.commit()
        conn.close()

    def update_category(self, id, fields):
        conn = get_db_connection()
        cursor = conn.cursor()
        set_clause = ", ".join([f"{key} = ?" for key in fields.keys()])
        values = list(fields.values()) + [id]
        cursor.execute(f"UPDATE Categories SET {set_clause} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def delete_category(self, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Categories WHERE id = ?", (id,))
        conn.commit()
        conn.close()

    def get_category(self, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Categories WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        return Category(row["id"], row["name"], row["description"]) if row else None

    def get_all_categories(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Categories")
        rows = cursor.fetchall()
        conn.close()
        return [Category(row["id"], row["name"], row["description"]) for row in rows]

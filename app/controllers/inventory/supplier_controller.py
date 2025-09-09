from app.DB.db import get_db_connection
from app.models.models_inventory.supplier import Supplier

class SupplierController:
    def create_supplier(self, supplier: Supplier):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Suppliers (company_name, contact_name, contact_email, address, city, country, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier.company_name,
            supplier.contact_name,
            supplier.contact_email,
            supplier.address,
            supplier.city,
            supplier.country,
            supplier.phone
        ))
        conn.commit()
        conn.close()

    def get_all_suppliers(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Suppliers")
        rows = cursor.fetchall()
        conn.close()
        return [Supplier(**row).to_dict() for row in rows]

    def get_supplier_by_id(self, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Suppliers WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Supplier(**row).to_dict()
        return None

    def update_supplier(self, id, updated_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Suppliers
            SET company_name = ?, contact_name = ?, contact_email = ?, address = ?, city = ?, country = ?, phone = ?
            WHERE id = ?
        """, (
            updated_data.get("company_name"),
            updated_data.get("contact_name"),
            updated_data.get("contact_email"),
            updated_data.get("address"),
            updated_data.get("city"),
            updated_data.get("country"),
            updated_data.get("phone"),
            id
        ))
        conn.commit()
        conn.close()

    def delete_supplier(self, id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Suppliers WHERE id = ?", (id,))
        conn.commit()
        conn.close()

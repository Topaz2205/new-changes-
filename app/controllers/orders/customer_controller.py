# app/controllers/orders/customer_controller.py

from app.DB.db import get_db_connection
from app.models.models_orders.customer import Customer

class CustomerController:
    def __init__(self):
        pass

    def create_customer(self, customer_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Customers (
                contact_name, contact_title, address, customer_type,
                customer_tag, city, postal_code, country, phone, email
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_data['contact_name'],
            customer_data.get('contact_title'),
            customer_data.get('address'),
            customer_data.get('customer_type'),
            customer_data.get('customer_tag'),
            customer_data.get('city'),
            customer_data.get('postal_code'),
            customer_data.get('country'),
            customer_data.get('phone'),
            customer_data.get('email')
        ))

        conn.commit()
        conn.close()

    def update_customer(self, customer_id, updated_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        fields = []
        values = []

        for key, value in updated_data.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(customer_id)

        cursor.execute(f"""
            UPDATE Customers
            SET {', '.join(fields)}
            WHERE customer_id = ?
        """, tuple(values))

        conn.commit()
        conn.close()

    def delete_customer(self, customer_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Customers WHERE customer_id = ?", (customer_id,))
        conn.commit()
        conn.close()

    def get_customer_orders(self, customer_id):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM Orders WHERE user_id = ?
        """, (customer_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

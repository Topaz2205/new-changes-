from app.DB.db import get_db_connection
from app.models.models_access.employee import Employee

class EmployeeController:
    def __init__(self):
        pass

    def create_employee(self, employee_data):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Employees (
                user_id, position, manager_id
            ) VALUES (?, ?, ?)
        """, (
            employee_data["user_id"],
            employee_data.get("position"),
            employee_data.get("manager_id")
        ))
        conn.commit()
        conn.close()

    def get_all_employees(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employees")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_employee_by_id(self, employee_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employees WHERE id = ?", (employee_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_employee(self, employee_id, updated_data):
        conn = get_db_connection()
        cursor = conn.cursor()

        fields = ', '.join(f"{key} = ?" for key in updated_data)
        values = list(updated_data.values()) + [employee_id]

        cursor.execute(f"""
            UPDATE Employees SET {fields} WHERE id = ?
        """, values)
        conn.commit()
        conn.close()

    def delete_employee(self, employee_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Employees WHERE id = ?", (employee_id,))
        conn.commit()
        conn.close()

    def get_subordinates(self, manager_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Employees WHERE manager_id = ?", (manager_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

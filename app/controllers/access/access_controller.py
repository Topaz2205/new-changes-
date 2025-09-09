from ...models.models_access.user import User
from ...models.models_access.role import Role
from ...models.models_access.permission import Permission
from ...models.models_access.employee import Employee
from app.DB.db import get_db_connection
from datetime import datetime

class AccessController:

    def get_all_users(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users")
        rows = cursor.fetchall()
        

        enriched_users = []
        for row in rows:
            user_dict = dict(row)

            # --- עיבוד created_at לפורמט אחיד ---
            created_at = user_dict.get("created_at")
            if created_at:
                try:
                    # אם כולל שבר שנייה
                    parsed_dt = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S.%f")
                except ValueError:
                    # אם לא כולל שבר שנייה
                    parsed_dt = datetime.strptime(str(created_at), "%Y-%m-%d %H:%M:%S")
                user_dict["created_at"] = parsed_dt.strftime("%Y-%m-%d %H:%M:%S")

            # --- הוספת הרשאות ---
            role_id = user_dict.get("role_id")
            permissions = self.get_permissions_by_role_id(role_id)
            user_dict["permissions"] = permissions

            # ✨ שליפת שם התפקיד מהטבלה Roles
            cursor.execute("SELECT name FROM Roles WHERE id = ?", (role_id,))
            role_row = cursor.fetchone()
            user_dict["role_name"] = role_row["name"] if role_row else "None"


            enriched_users.append(user_dict)
        conn.close()
        return enriched_users



    def add_user(self, username, email, password, role):
        conn = get_db_connection()
        cursor = conn.cursor()
        created_at = datetime.now()
        cursor.execute("""
            INSERT INTO Users (username, email, password, role_id, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, password, role, created_at))
        conn.commit()
        conn.close()

    def get_all_roles(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Roles")
        rows = cursor.fetchall()
        conn.close()
        return [Role(**dict(row)).to_dict() for row in rows]

    def add_role(self, name, description):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Roles (name, description)
            VALUES (?, ?)
        """, (name, description))
        conn.commit()
        conn.close()

    def get_all_permissions(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Permissions")
        rows = cursor.fetchall()
        conn.close()
        return [Permission(**dict(row)).to_dict() for row in rows]

    def add_permission(self, name, description):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Permissions (name, description)
            VALUES (?, ?)
        """, (name, description))
        conn.commit()
        conn.close()

    def get_user_by_credentials(self, username, password):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Users WHERE username = ? AND password = ?
        """, (username, password))
        row = cursor.fetchone()
        conn.close()

        if row:
            return User(**dict(row))
        return None

    def get_user_by_id(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return User(**dict(row)).to_dict()
        return None

    def update_user(self, user_id, username, email, password, role_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Users
            SET username = ?, email = ?, password = ?, role_id = ?
            WHERE id = ?
        """, (username, email, password, role_id, user_id))
        conn.commit()
        conn.close()

    def delete_user(self, user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

    def get_role_name_by_id(self, role_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Roles WHERE id = ?", (role_id,))
        row = cursor.fetchone()
        conn.close()
        return row["name"] if row else None

    def get_permissions_by_role(self, role_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name FROM Permissions p
            JOIN RolePermissions rp ON p.id = rp.permission_id
            JOIN Roles r ON r.id = rp.role_id
            WHERE r.name = ?
        """, (role_name,))
        rows = cursor.fetchall()
        conn.close()
        return [row["name"] for row in rows]

    def get_permissions_by_role_id(self, role_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.name FROM Permissions p
            JOIN RolePermissions rp ON p.id = rp.permission_id
            WHERE rp.role_id = ?
        """, (role_id,))
        rows = cursor.fetchall()
        conn.close()
        return [row["name"] for row in rows]

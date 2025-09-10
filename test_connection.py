# test_connection.py
import os
from dotenv import load_dotenv

load_dotenv()

from app.DB.db import get_db_connection

def main():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # מחזיר dict: {'current_database': 'ordersync', 'current_user': 'ordersync_user', 'version': 'PostgreSQL ...'}
                cur.execute("SELECT current_database() AS current_database, current_user AS current_user, version() AS version")
                row = cur.fetchone()
                dbname = row["current_database"]
                user = row["current_user"]
                version = row["version"]
                print(f"✅ Connected to Postgres! db={dbname}, user={user}")
                print(version)

                # רשימת טבלאות
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY 1
                    LIMIT 50
                """)
                tables = [r["table_name"] for r in cur.fetchall()]
                print("Tables:", tables if tables else "— none —")

    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    main()

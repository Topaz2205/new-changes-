# test_connection.py
from app.DB import db

def main():
    try:
        # ניסיון להריץ שאילתה פשוטה
        row = db.query_one("SELECT version();")
        print("✅ Connected to Postgres!")
        print("Postgres version:", row["version"])
    except Exception as e:
        print("❌ Connection failed:", e)

if __name__ == "__main__":
    main()

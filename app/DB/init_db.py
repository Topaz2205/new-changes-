import sqlite3
import os

# נתיב בסיס לתיקייה שבה נמצאים הקבצים
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# קבצי SQL נפרדים
CREATE_FILE = os.path.join(BASE_DIR, "final_create_tables.sql")
INSERT_FILE = os.path.join(BASE_DIR, "insert_data.sql")
DB_FILE = os.path.join(BASE_DIR, "database.db")


def execute_sql_file(cursor, filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            sql_script = file.read()

        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        for i, statement in enumerate(statements, start=1):
            try:
                cursor.execute(statement)
            except sqlite3.IntegrityError as e:
                print(f"\n❌ IntegrityError in {os.path.basename(filepath)} - Statement #{i}:\n👉 {e}")
                print(f"📝 SQL:\n{statement}\n")
                raise  # עצור מיידית (אפשר גם לדלג ולהמשיך אם תרצה)
            except sqlite3.OperationalError as e:
                print(f"\n❌ OperationalError in {os.path.basename(filepath)} - Statement #{i}:\n👉 {e}")
                print(f"📝 SQL:\n{statement}\n")
                raise
            except Exception as e:
                print(f"\n❌ Unknown Error in {os.path.basename(filepath)} - Statement #{i}:\n👉 {e}")
                print(f"📝 SQL:\n{statement}\n")
                raise

        print(f"✅ Executed {os.path.basename(filepath)} successfully.")
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")


def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"🗑️ Existing {DB_FILE} deleted.")

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    execute_sql_file(cursor, CREATE_FILE)
    execute_sql_file(cursor, INSERT_FILE)

    conn.commit()
    conn.close()
    print("📦 Database created and initialized.")


if __name__ == "__main__":
    init_db()

import sqlite3
import os
from app.config import Config

def get_db_connection():
    db_path = Config.DB_FILE

    # ודא שהקובץ באמת קיים לפני חיבור
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found at: {db_path}")

    print("Connecting to database at:", db_path)  # שורת בדיקה

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # לוודא שיחסי גומלין בין טבלאות מופעלים
    conn.execute("PRAGMA foreign_keys = ON")

    return conn

#thanks 
#hello

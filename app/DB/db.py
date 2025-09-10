# app/DB/db.py
import os
import re
import contextlib
from typing import Any, Iterable

# --- טעינת ENV (אופציונלי, אם יש לך כבר טוען ENV אז אפשר להסיר) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower().strip()   # 'sqlite' or 'postgres'

# --- חיבורי DB לשני העולמות ---
if DB_BACKEND == "postgres":
    import psycopg2
    import psycopg2.extras

    def _connect():
        # קריאת פרמטרים מה-ENV
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        dbname = os.getenv("DB_NAME", "ordersync")
        user = os.getenv("DB_USER", "ordersync_user")
        password = os.getenv("DB_PASSWORD", "")
        sslmode = os.getenv("DB_SSLMODE", "require")  # בענן מומלץ require
        return psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password,
            sslmode=sslmode, cursor_factory=psycopg2.extras.RealDictCursor
        )
else:
    import sqlite3
    sqlite3.register_adapter(bool, int)

    def _connect():
        db_file = os.getenv("SQLITE_PATH", "app/DB/database.db")
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute("PRAGMA foreign_keys=ON;")
        return conn

# --- ממיר placeholder-ים: '?' -> '%s' (מתחשב במרכאות כדי לא לגעת בשאלות בתוך סטרינגים) ---
_qmark_pattern = re.compile(r"\?")

def _convert_qmark_to_psycopg(sql: str) -> str:
    # נעבור תו-תוו וננתק '?' שנמצאות בתוך מחרוזות ('...' או "...")
    out = []
    in_single = False
    in_double = False
    escape = False
    for ch in sql:
        if ch == "\\" and not escape:
            escape = True
            out.append(ch)
            continue
        if ch == "'" and not in_double and not escape:
            in_single = not in_single
            out.append(ch)
            continue
        if ch == '"' and not in_single and not escape:
            in_double = not in_double
            out.append(ch)
            continue
        if ch == "?" and not in_single and not in_double:
            out.append("%s")
        else:
            out.append(ch)
        escape = False
    return "".join(out)

# --- ממשק עבודה אחיד ---

@contextlib.contextmanager
def get_db_connection():
    conn = _connect()
    try:
        yield conn
        # ב-psycopg2 צריך לעשות commit ידני אם עבדנו עם cursor.execute()
        if DB_BACKEND == "postgres":
            conn.commit()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()

def execute(sql: str, params: Iterable[Any] | None = None):
    """
    הרצת שאילתה (INSERT/UPDATE/DELETE/DDL). ממשיך לאפשר כתיבת SQL עם '?' בכל הקוד.
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_conv = _convert_qmark_to_psycopg(sql)
            cur = conn.cursor()
            cur.execute(sql_conv, tuple(params or []))
            return cur
        else:
            cur = conn.execute(sql, tuple(params or []))
            return cur

def query_all(sql: str, params: Iterable[Any] | None = None):
    """
    SELECT שמחזיר רשימת שורות (list of dict-like rows).
    """
    cur = execute(sql, params)
    rows = cur.fetchall()
    # הפעלה אחידה: גם ב-sqlite (Row) וגם ב-psycopg (dict)
    return [dict(r) for r in rows]

def query_one(sql: str, params: Iterable[Any] | None = None):
    """
    SELECT שמחזיר שורה אחת או None.
    """
    cur = execute(sql, params)
    row = cur.fetchone()
    return dict(row) if row else None

def insert_and_get_id(sql: str, params: Iterable[Any] | None = None, pk_column: str = "id"):
    """
    הכנסה לטבלה והחזרת המפתח שנוצר.
    - ב-SQLite נשתמש ב-lastrowid.
    - ב-Postgres: אם ה-SQL שלך מכיל RETURNING, נחזיר ממנו; אחרת ננסה להוציא lastval().
      מומלץ: כשהטבלה ב-Postgres מוגדרת SERIAL/BIGSERIAL, תשתמש ב:
      INSERT ... VALUES (...) RETURNING <pk_column>;
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_conv = _convert_qmark_to_psycopg(sql)
            cur = conn.cursor()
            cur.execute(sql_conv, tuple(params or []))
            try:
                # אם יש RETURNING
                row = cur.fetchone()
                if row and pk_column in row:
                    return row[pk_column]
                # או אם החזרת ערך יחיד
                if row and len(row) == 1:
                    return list(row.values())[0]
            except Exception:
                pass
            # fallback (לא תמיד עובד אם אין SEQUENCE ברירת מחדל)
            cur2 = conn.cursor()
            cur2.execute("SELECT lastval() AS last_id;")
            r2 = cur2.fetchone()
            return r2["last_id"] if r2 else None
        else:
            cur = conn.execute(sql, tuple(params or []))
            return cur.lastrowid

def run_sql_script(path: str):
    sql = open(path, "r", encoding="utf-8").read()
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            # פיצול נאיבי לפקודות; עדיף להריץ קובצי Postgres ייעודיים (ללא PRAGMA וכו')
            for stmt in sql.split(";"):
                s = stmt.strip()
                if s:
                    execute(s)
        else:
            conn.executescript(sql)

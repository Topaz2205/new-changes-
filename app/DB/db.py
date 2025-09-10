# app/DB/db.py
# ------------------------------------------------------------
# מודול גנרי לעבודה מול SQLite/Postgres עם אותו API
# - טוען .env (אם קיים)
# - בוחר דיאלקט לפי DB_BACKEND=sqlite|postgres
# - ממיר אוטומטית סימני שאלה '?' ל-%s ב-Postgres
# - לא מחזיר cursor מחוץ ל-context (מונע "cursor already closed")
# ------------------------------------------------------------

import os
import re
import contextlib
from typing import Any, Iterable, Optional

# --- טעינת ENV (אופציונלי) ---
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower().strip()   # 'sqlite' או 'postgres'

# ------------------------------------------------------------
# עוזר: הסרת הערות SQL לפני המרת '?'
#   מטפל ב- -- עד סוף שורה, וב- /* ... */ רב-שורות
# ------------------------------------------------------------
_comment_line = re.compile(r"--.*?$", re.MULTILINE | re.DOTALL)
_comment_block = re.compile(r"/\*.*?\*/", re.DOTALL)

def _strip_sql_comments(sql: str) -> str:
    sql = re.sub(_comment_block, "", sql)
    sql = re.sub(_comment_line, "", sql)
    return sql

# ------------------------------------------------------------
# המרה בטוחה יחסית של '?' ל- %s (לא נוגעת בשאלות בתוך מחרוזות / dollar-quoted)
# ------------------------------------------------------------
def _convert_qmark_to_psycopg(sql: str) -> str:
    out: list[str] = []
    in_single = False
    in_double = False
    in_dollar: Optional[str] = None  # לדולר-קואוטים $$label$$
    i = 0
    while i < len(sql):
        ch = sql[i]

        # זיהוי תחילת/סיום דולר-קואוט $$ or $tag$
        if not in_single and not in_double:
            if in_dollar is None and ch == "$":
                j = i + 1
                while j < len(sql) and (sql[j].isalnum() or sql[j] == "_"):
                    j += 1
                if j < len(sql) and sql[j] == "$":
                    in_dollar = sql[i:j+1]  # כגון "$$" או "$tag$"
                    out.append(in_dollar)
                    i = j + 1
                    continue
            elif in_dollar is not None and sql.startswith(in_dollar, i):
                out.append(in_dollar)
                i += len(in_dollar)
                in_dollar = None
                continue

        if in_dollar is None:
            if ch == "'" and not in_double:
                in_single = not in_single
                out.append(ch)
                i += 1
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                out.append(ch)
                i += 1
                continue

        if ch == "?" and not in_single and not in_double and in_dollar is None:
            out.append("%s")
        else:
            out.append(ch)
        i += 1
    return "".join(out)

# ------------------------------------------------------------
# חיבורי DB
# ------------------------------------------------------------
if DB_BACKEND == "postgres":
    import psycopg2
    import psycopg2.extras

    def _connect():
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        dbname = os.getenv("DB_NAME", "ordersync")
        user = os.getenv("DB_USER", "ordersync_user")
        password = os.getenv("DB_PASSWORD", "")
        sslmode = os.getenv("DB_SSLMODE", "require")
        return psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode,
            cursor_factory=psycopg2.extras.RealDictCursor,  # החזר dict
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

# ------------------------------------------------------------
# ממשק עבודה אחיד
# ------------------------------------------------------------
@contextlib.contextmanager
def get_db_connection():
    """
    מניב Connection פתוח בתוך context, וסוגר/מגלגל חזרה בסיום.
    אין להחזיר cursor מחוץ ל-context.
    """
    conn = _connect()
    try:
        yield conn
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

def execute(sql: str, params: Iterable[Any] | None = None) -> int:
    """
    הרצת שאילתה (INSERT/UPDATE/DELETE/DDL).
    מחזיר rowcount. לא מחזיר cursor (כדי לא להחזיק אובייקטים אחרי סגירת החיבור).
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                return cur.rowcount
        else:
            # sqlite
            cur = conn.execute(sql, tuple(params or []))
            return cur.rowcount

def query_all(sql: str, params: Iterable[Any] | None = None) -> list[dict]:
    """
    מבצע SELECT ומחזיר רשימת dict-ים.
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                rows = cur.fetchall()  # RealDictRow -> dict
                return list(rows)
        else:
            cur = conn.execute(sql, tuple(params or []))
            rows = cur.fetchall()
            return [dict(r) for r in rows]

def query_one(sql: str, params: Iterable[Any] | None = None) -> Optional[dict]:
    """
    מבצע SELECT ומחזיר dict אחד או None.
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                row = cur.fetchone()
                return dict(row) if row else None
        else:
            cur = conn.execute(sql, tuple(params or []))
            row = cur.fetchone()
            return dict(row) if row else None

def insert_and_get_id(
    sql: str,
    params: Iterable[Any] | None = None,
    pk_column: str = "id",
    *,
    table_for_currval: str | None = None
):
    """
    הכנסת רשומה והחזרת המפתח שנוצר.
    ב-Postgres: מומלץ לכלול RETURNING <pk> ב-SQL.
    אם אין RETURNING ונמסר table_for_currval, ננסה currval(pg_get_serial_sequence(...)).
    """
    with get_db_connection() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                # 1) עדיפות ל-RETURNING
                try:
                    row = cur.fetchone()
                    if row:
                        if pk_column in row:
                            return row[pk_column]
                        if len(row) == 1:
                            return list(row.values())[0]
                except Exception:
                    pass
            # 2) currval אם נמסר table_for_currval
            if table_for_currval:
                with conn.cursor() as cur2:
                    cur2.execute(
                        "SELECT currval(pg_get_serial_sequence(%s, %s)) AS last_id;",
                        (table_for_currval, pk_column),
                    )
                    r2 = cur2.fetchone()
                    if r2 and "last_id" in r2:
                        return r2["last_id"]
            # 3) fallback אחרון (לא תמיד בטוח אם יש טריגרים/ריסיקוונסים מרובים)
            with conn.cursor() as cur3:
                cur3.execute("SELECT lastval() AS last_id;")
                r3 = cur3.fetchone()
                return r3["last_id"] if r3 else None
        else:
            cur = conn.execute(sql, tuple(params or []))
            return cur.lastrowid

def run_sql_script(path: str):
    """
    הרצת קובץ SQL (פשוט). לסקריפטים גדולים/מורכבים עדיף להשתמש ב-psql -f.
    """
    sql = open(path, "r", encoding="utf-8").read()
    if DB_BACKEND == "postgres":
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    else:
        with get_db_connection() as conn:
            conn.executescript(sql)

# ------------------------------------------------------------
# כלי עזר קטנים
# ------------------------------------------------------------
def ping() -> bool:
    """
    בודק חיבור בסיסי ל-DB.
    """
    try:
        if DB_BACKEND == "postgres":
            return query_one("SELECT 1 AS ok") is not None
        else:
            return query_one("SELECT 1 AS ok") is not None
    except Exception:
        return False

def backend_name() -> str:
    return DB_BACKEND

# app/DB/db.py
# ------------------------------------------------------------
# מודול גנרי לעבודה מול SQLite/Postgres עם אותו API
# - טוען .env (אם קיים)
# - בוחר דיאלקט לפי DB_BACKEND=sqlite|postgres
# - ממיר אוטומטית '?' ל-%s ב-Postgres
# - get_db_connection מחזיר חיבור רגיל (לא contextmanager)
# - db_context הוא ה-contextmanager לשימוש פנימי בפונקציות העזר
# ------------------------------------------------------------

import os
import re
import contextlib
from typing import Any, Iterable, Optional

# --- טעינת ENV (אופציונלי) ---
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower().strip()   # 'sqlite' או 'postgres'

# ------------------------------------------------------------
# עוזר: הסרת הערות SQL לפני המרת '?'
# ------------------------------------------------------------
_comment_line = re.compile(r"--.*?$", re.MULTILINE | re.DOTALL)
_comment_block = re.compile(r"/\*.*?\*/", re.DOTALL)

def _strip_sql_comments(sql: str) -> str:
    sql = re.sub(_comment_block, "", sql)
    sql = re.sub(_comment_line, "", sql)
    return sql

# ------------------------------------------------------------
# המרה בטוחה יחסית של '?' ל- %s (לא נוגעת במחרוזות / dollar-quoted)
# ------------------------------------------------------------
def _convert_qmark_to_psycopg(sql: str) -> str:
    out: list[str] = []
    in_single = False
    in_double = False
    in_dollar: Optional[str] = None
    i = 0
    while i < len(sql):
        ch = sql[i]

        # זיהוי $$ או $tag$
        if not in_single and not in_double:
            if in_dollar is None and ch == "$":
                j = i + 1
                while j < len(sql) and (sql[j].isalnum() or sql[j] == "_"):
                    j += 1
                if j < len(sql) and sql[j] == "$":
                    in_dollar = sql[i:j+1]
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
                out.append(ch); i += 1; continue
            if ch == '"' and not in_single:
                in_double = not in_double
                out.append(ch); i += 1; continue

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
    import psycopg2  # type: ignore
    import psycopg2.extras  # type: ignore

    # --- עטיפות ל-Postgres: המרת '?' ל-%s בכל execute/executemany ---
    class _PGCursorWrapper:
        def __init__(self, cur):
            self._cur = cur

        def execute(self, sql, params=None):
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            if params is None:
                return self._cur.execute(sql_conv)
            return self._cur.execute(sql_conv, tuple(params))

        def executemany(self, sql, seq_of_params):
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            return self._cur.executemany(sql_conv, [tuple(p) for p in (seq_of_params or [])])

        def __enter__(self):
            self._cur.__enter__()
            return self

        def __exit__(self, *args):
            return self._cur.__exit__(*args)

        def __getattr__(self, name):
            return getattr(self._cur, name)

    class _PGConnectionWrapper:
        def __init__(self, conn):
            self._conn = conn

        def cursor(self, *args, **kwargs):
            real = self._conn.cursor(*args, **kwargs)
            return _PGCursorWrapper(real)

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def close(self):
            return self._conn.close()

    def _connect():
        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "5432"))
        dbname = os.getenv("DB_NAME", "ordersync")
        user = os.getenv("DB_USER", "ordersync_user")
        password = os.getenv("DB_PASSWORD", "")
        sslmode = os.getenv("DB_SSLMODE", "require")
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
            sslmode=sslmode,
            cursor_factory=psycopg2.extras.RealDictCursor,  # החזר dict
        )
        return _PGConnectionWrapper(conn)

else:
    import sqlite3
    sqlite3.register_adapter(bool, int)

    def _connect():
        db_file = os.getenv("SQLITE_PATH", "app/DB/database.db")
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        with conn:
            conn.execute("PRAGMA foreign_keys=ON;")
        return conn

# ------------------------------------------------------------
# API כפול: get_db_connection (חיבור רגיל) + db_context (ניהול אוטומטי)
# ------------------------------------------------------------
def get_db_connection():
    """
    מחזיר אובייקט חיבור אמיתי (לא contextmanager),
    כדי שקוד קיים יעבוד: conn = get_db_connection(); conn.cursor()
    """
    return _connect()

@contextlib.contextmanager
def db_context():
    """
    Context manager לעבודה בטוחה עם חיבור (commit/rollback/close אוטומטי).
    משמש את פונקציות העזר בתוך המודול.
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

# ------------------------------------------------------------
# ממשק עבודה אחיד (משתמש ב-db_context)
# ------------------------------------------------------------
def execute(sql: str, params: Iterable[Any] | None = None) -> int:
    """INSERT/UPDATE/DELETE/DDL. מחזיר rowcount."""
    with db_context() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                return cur.rowcount
        else:
            cur = conn.execute(sql, tuple(params or []))
            return cur.rowcount

def query_all(sql: str, params: Iterable[Any] | None = None) -> list[dict]:
    """SELECT מרובה. מחזיר רשימת dict-ים."""
    with db_context() as conn:
        if DB_BACKEND == "postgres":
            sql_no_comments = _strip_sql_comments(sql)
            sql_conv = _convert_qmark_to_psycopg(sql_no_comments)
            with conn.cursor() as cur:
                cur.execute(sql_conv, tuple(params or []))
                rows = cur.fetchall()
                return list(rows)
        else:
            cur = conn.execute(sql, tuple(params or []))
            rows = cur.fetchall()
            return [dict(r) for r in rows]

def query_one(sql: str, params: Iterable[Any] | None = None) -> Optional[dict]:
    """SELECT יחיד. מחזיר dict או None."""
    with db_context() as conn:
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
    ב-Postgres: עדיף לכלול RETURNING <pk>. אם לא—ננסה currval/lastval לפי הצורך.
    """
    with db_context() as conn:
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
            # 3) fallback אחרון
            with conn.cursor() as cur3:
                cur3.execute("SELECT lastval() AS last_id;")
                r3 = cur3.fetchone()
                return r3["last_id"] if r3 else None
        else:
            cur = conn.execute(sql, tuple(params or []))
            return cur.lastrowid

def run_sql_script(path: str):
    """הרצת קובץ SQL שלם."""
    sql = open(path, "r", encoding="utf-8").read()
    if DB_BACKEND == "postgres":
        with db_context() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
    else:
        with db_context() as conn:
            conn.executescript(sql)

# ------------------------------------------------------------
# כלי עזר
# ------------------------------------------------------------
def ping() -> bool:
    try:
        return query_one("SELECT 1 AS ok") is not None
    except Exception:
        return False

def backend_name() -> str:
    return DB_BACKEND

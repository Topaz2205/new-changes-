import sys, sqlite3, pathlib

def run_sql(db_path: str, sql_path: str):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    sql = pathlib.Path(sql_path).read_text(encoding="utf-8")
    try:
        db.executescript(sql)
        db.commit()
        print(f"OK: ran {sql_path} against {db_path}")
    except Exception as e: 
        db.rollback()
        print(f"ERROR running {sql_path}: {e}")
        raise
    finally:
        db.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python run_sql.py <path/to/database.db> <sql1.sql> [<sql2.sql> ...]")
        sys.exit(1)
    db_path = sys.argv[1]
    for sql_path in sys.argv[2:]:
        run_sql(db_path, sql_path)

if __name__ == "__main__":
    main()

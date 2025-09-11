import os, json, time
import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv, find_dotenv
import requests
import faiss

# ---- config ----
BASE_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE_DIR, "index.faiss")
META_PATH  = os.path.join(BASE_DIR, "meta.json")
EMBED_MODEL = "nomic-embed-text"
BATCH = 64

# --- NEW: load .env from project root and app/ai/.env ---
def _load_env():
    try:
        root_env = find_dotenv(filename=".env", raise_error_if_not_found=False)
        if root_env:
            load_dotenv(root_env, override=False)
    except Exception:
        pass
    load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

def embed_texts(texts):
    """
    שולח טקסטים ל-Ollama לקבל embedding (וקטור).
    """
    url = "http://localhost:11434/api/embeddings"
    out = []
    for i in range(0, len(texts), BATCH):
        chunk = texts[i:i+BATCH]
        resp = requests.post(url, json={"model": EMBED_MODEL, "input": chunk}, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        # Ollama מחזיר {"embeddings": [[...], [...]]} או {"embedding":[...]} – נורמליזציה:
        if "embeddings" in data:
            vecs = data["embeddings"]
        else:
            vecs = [data["embedding"]]
        out.extend(vecs)
    return np.array(out, dtype="float32")

def connect_pg():
    # --- NEW: support DB_* or PG_* and load both env files ---
    _load_env()
    host    = os.getenv("DB_HOST")     or os.getenv("PG_HOST")
    port    = os.getenv("DB_PORT")     or os.getenv("PG_PORT") or "5432"
    dbname  = os.getenv("DB_NAME")     or os.getenv("PG_DB")   or "postgres"
    user    = os.getenv("DB_USER")     or os.getenv("PG_USER")
    pwd     = os.getenv("DB_PASSWORD") or os.getenv("PG_PASSWORD")
    sslmode = os.getenv("DB_SSLMODE")  or "require"

    if not all([host, user, pwd]):
        raise RuntimeError("חסרים פרטי חיבור (DB_HOST/DB_USER/DB_PASSWORD או PG_HOST/PG_USER/PG_PASSWORD).")

    print(f"🔌 Connecting to {host}:{port}/{dbname} as {user} (sslmode={sslmode})")
    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=pwd,
        sslmode=sslmode,
    )
    return conn

def fetch_rows(conn):
    """
    תביא מידע תמציתי מהטבלאות המרכזיות.
    אם יש לך שמות מעט שונים – עדכן כאן.
    """
    q = {
        "products": """
            SELECT product_id, name, sku, supplier_id, category_id
            FROM Products
            ORDER BY product_id
            LIMIT 5000;
        """,
        "inventory": """
            SELECT product_id, quantity, threshold
            FROM Inventory
            ORDER BY product_id
            LIMIT 5000;
        """,
        "orders": """
            SELECT order_id, customer_id, status, created_at
            FROM Orders
            ORDER BY order_id DESC
            LIMIT 5000;
        """,
        "shipments": """
            SELECT shipment_id, order_id, status, tracking_number, estimated_delivery
            FROM Shipments
            ORDER BY shipment_id DESC
            LIMIT 5000;
        """,
        "order_updates": """
            SELECT update_id, order_id, update_type, old_value, new_value, updated_at
            FROM OrderUpdates
            ORDER BY updated_at DESC
            LIMIT 5000;
        """,
        "customers": """
            SELECT customer_id, name, email
            FROM Customers
            ORDER BY customer_id
            LIMIT 5000;
        """
    }

    all_records = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for kind, sql in q.items():
            cur.execute(sql)
            rows = cur.fetchall()
            for r in rows:
                # בנה טקסט קריא קצר (chunk)
                text = f"[{kind}] " + " | ".join(f"{k}={r[k]}" for k in r if r[k] is not None)
                all_records.append({
                    "kind": kind,
                    "id": r.get("order_id") or r.get("product_id") or r.get("shipment_id") or r.get("update_id") or r.get("customer_id"),
                    "text": text
                })
    return all_records

def build_or_update_index(records):
    texts = [r["text"] for r in records]

    # --- NEW: if empty, still write an empty index & meta to avoid 500s ---
    if not texts:
        print("⚠️ No records found. Writing an empty index so the API won't 500.")
        # השג ממד ע״י אמבדינג למילה אחת
        vec = embed_texts(["placeholder"])
        if vec.ndim != 2:
            raise RuntimeError(f"Unexpected embeddings shape: {vec.shape}")
        d = vec.shape[1]
        faiss.normalize_L2(vec)
        index = faiss.IndexFlatIP(d)
        # אינדקס ריק (לא מוסיפים וקטורים)
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        print(f"✅ Saved EMPTY index to {INDEX_PATH} and {META_PATH}")
        return

    print(f"Embedding {len(texts)} chunks…")
    vecs = embed_texts(texts)  # (N, D)
    d = vecs.shape[1]

    index = faiss.IndexFlatIP(d)  # cosine-like אם ננרמל
    # נרמול לווקטורים ליחידה:
    faiss.normalize_L2(vecs)
    index.add(vecs)

    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False)
    print(f"✅ Saved index to {INDEX_PATH} and {META_PATH}")

def main():
    t0 = time.time()
    with connect_pg() as conn:
        records = fetch_rows(conn)
    build_or_update_index(records)
    print(f"Done in {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()

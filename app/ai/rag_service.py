# app/ai/rag_service.py
import os, json, re
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import faiss
import psycopg2
import requests
from psycopg2.extras import RealDictCursor

# ---------- Paths / Models ----------
AI_DIR     = os.path.dirname(__file__)
INDEX_PATH = os.path.join(AI_DIR, "index.faiss")
META_PATH  = os.path.join(AI_DIR, "meta.json")

EMBED_MODEL     = os.getenv("EMBED_MODEL", "nomic-embed-text")
GEN_MODEL       = os.getenv("GEN_MODEL",   "qwen2:1.5b-instruct")
OLLAMA_BASE     = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_TIMEOUT  = float(os.getenv("OLLAMA_TIMEOUT", "300"))

TOP_K           = int(os.getenv("TOP_K", "3"))
CTX_CHARS       = int(os.getenv("CTX_CHARS", "320"))
GEN_MAX_TOKENS  = int(os.getenv("GEN_MAX_TOKENS", "128"))
GEN_TEMPERATURE = float(os.getenv("GEN_TEMPERATURE", "0.2"))

# ---------- DB env (PG_* או DB_*) ----------
PGHOST     = os.getenv("PGHOST")     or os.getenv("DB_HOST")
PGPORT     = int(os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432")
PGDATABASE = os.getenv("PGDATABASE") or os.getenv("DB_NAME")
PGUSER     = os.getenv("PGUSER")     or os.getenv("DB_USER")
PGPASSWORD = os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD")
PGSSLMODE  = os.getenv("PGSSLMODE")  or os.getenv("DB_SSLMODE") or "require"

# DB-first כ־ברירת מחדל
RAG_DB_FIRST = True

# ---------- הגדרות קומפקטיות ----------
ENTITY_TABLES = {
    "order":     "orders",
    "shipment":  "shipments",
    "product":   "products",
    "customer":  "customers",
    "supplier":  "suppliers",
    "category":  "categories",
    "inventory": "inventory",
}

# מילון קצר של “תפקידים” -> שמות עמודות אפשריים
FIELD_SYNONYMS = {
    "id":              ["id", "order_id", "shipment_id", "product_id", "customer_id", "supplier_id", "category_id"],
    "name":            ["name", "full_name", "product_name", "category_name", "title"],
    "status":          ["status", "state", "order_status", "shipment_status"],
    "created_ts":      ["created_at", "ordered_at", "order_date", "createdon", "createdat"],
    "updated_ts":      ["updated_at"],
    # קשרים
    "order_fk":        ["order_id", "orderid", "order"],
    "product_fk":      ["product_id", "productid", "product"],
    "customer_fk":     ["customer_id", "customerid", "customer"],
    # משלוחים
    "tracking_number": ["tracking_number", "trackingnumber", "tracking_no", "tracking"],
    "carrier":         ["carrier", "shipping_company", "vendor", "shipper"],
    "shipped_ts":      ["shipped_at", "ship_date", "shippedat"],
    # מלאי
    "quantity":        ["quantity", "qty", "stock", "available", "available_quantity", "on_hand"],
    "sku":             ["sku", "code"],
    "price":           ["price", "unit_price", "cost"],
}

INTENT_KEYWORDS = {
    "order":     ["הזמנה", "order"],
    "shipment":  ["משלוח", "shipment", "tracking", "מספר מעקב"],
    "product":   ["מוצר", "product"],
    "inventory": ["מלאי", "stock", "inventory", "כמות"],
    "customer":  ["לקוח", "customer"],
    "supplier":  ["ספק", "supplier"],
    "category":  ["קטגוריה", "קטגוריות", "category", "categories"],
}

class RAGService:
    """DB-first כללי ישויות נפוצות; RAG fallback תמציתי."""

    def __init__(self) -> None:
        self.index = None
        self.meta: List[Dict[str, Any]] = []
        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            try:
                self.index = faiss.read_index(INDEX_PATH)
                with open(META_PATH, "r", encoding="utf-8") as f:
                    self.meta = json.load(f)
            except Exception as e:
                print("⚠️ FAISS/meta load error:", e)

    # -------- Public --------
    def health(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{OLLAMA_BASE}/api/version", timeout=3)
            return {"ok": r.ok, "version": r.json() if r.ok else r.text}
        except Exception as e:
            return {"ok": False, "version": f"error: {e}"}

    def ask(self, query: str, top_k: Optional[int] = None, ctx_chars: Optional[int] = None,
            db_first: Optional[bool] = None, **_: Any) -> Dict[str, Any]:
        q = (query or "").strip()
        if not q:
            return {"ok": False, "answer": "שאלה ריקה."}

        k = TOP_K if top_k is None else max(0, int(top_k))
        c = CTX_CHARS if ctx_chars is None else max(0, int(ctx_chars))
        use_db = RAG_DB_FIRST if db_first is None else bool(db_first)

        # --- DB-FIRST קטנטן וגמיש ---
        if use_db:
            entity = self._detect_intent(q)
            if entity:
                ent_id  = self._extract_id(q, INTENT_KEYWORDS[entity])
                ent_txt = self._extract_name(q, INTENT_KEYWORDS[entity])
                ok, payload = self._db_answer(entity, ent_id, ent_txt)
                # אם הצליח או שאין תוצאה/שגיאת DB — החזר ונעצור
                if ok:
                    return {"ok": True, "answer": payload["text"]}
                if payload.get("kind") in ("db_not_found", "db_error"):
                    return {"ok": payload["kind"] != "db_error", "answer": payload["msg"]}

        # --- RAG fallback קצר ---
        try:
            ctx, hits = self._retrieve_with_hits(q, k, c)
            prompt = self._build_prompt(q, ctx)
            ans = self._generate(prompt)
            sources = [{"rank": i+1, "kind": h.get("kind"), "id": h.get("id"), "score": float(h.get("score", 0.0))}
                       for i, h in enumerate(hits)]
            return {"ok": True, "answer": ans, "sources": sources}
        except Exception as e:
            return {"ok": False, "answer": f"שגיאת מודל/אחזור: {e}"}

    # -------- Intent & parsing --------
    def _detect_intent(self, text: str) -> Optional[str]:
        t = text.lower()
        for ent, keys in INTENT_KEYWORDS.items():
            if any(k.lower() in t for k in keys):
                return ent
        # אם לא מצאנו—מקרה פרקטי: אם כתבו "order 5" או "מוצר 7"
        if re.search(r"\border\b", t): return "order"
        if re.search(r"\bproduct\b", t): return "product"
        return None

    @staticmethod
    def _extract_id(text: str, keys: List[str]) -> Optional[int]:
        pat = r"(?:%s)\D*?(\d{1,10})" % "|".join([re.escape(k) for k in keys])
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try: return int(m.group(1))
            except: pass
        m2 = re.search(r"\b(\d{1,10})\b", text)
        if m2:
            try: return int(m2.group(1))
            except: pass
        return None

    @staticmethod
    def _extract_name(text: str, keys: List[str]) -> Optional[str]:
        m = re.search(r"\"([^\"]{2,64})\"|'([^']{2,64})'", text)
        if m: return (m.group(1) or m.group(2)).strip()
        for k in keys:
            m2 = re.search(rf"{re.escape(k)}\s+([A-Za-z0-9\u0590-\u05FF][^?.,:;]{1,64})", text)
            if m2: return m2.group(1).strip()
        return None

    # -------- DB helpers --------
    def _pg(self):
        if not PGHOST or not PGDATABASE or not PGUSER:
            raise RuntimeError("DB env not set")
        return psycopg2.connect(host=PGHOST, port=PGPORT, dbname=PGDATABASE,
                                user=PGUSER, password=PGPASSWORD, sslmode=PGSSLMODE)

    def _cols(self, conn, table: str) -> Dict[str, str]:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = current_schema() AND table_name = %s
            """, [table])
            cols = [r["column_name"] for r in cur.fetchall()]
        return {c.lower(): c for c in cols}

    @staticmethod
    def _pick(cols: Dict[str, str], role: str) -> Optional[str]:
        for cand in FIELD_SYNONYMS.get(role, []):
            if cols.get(cand.lower()):
                return cols[cand.lower()]
        return None

    # -------- DB answer (GENERIC + שני מקרים קצרים) --------
    def _db_answer(self, entity: str, ent_id: Optional[int], ent_name: Optional[str]) -> Tuple[bool, Dict[str, Any]]:
        table = ENTITY_TABLES.get(entity)
        if not table:
            return False, {"kind": "db_not_found", "msg": "לא נמצאה ישות מתאימה."}
        try:
            with self._pg() as conn:
                cols = self._cols(conn, table)
                if not cols:
                    return False, {"kind": "db_error", "msg": f"טבלת {table} לא נמצאה."}

                # שדות נפוצים לכולם:
                f_id   = self._pick(cols, "id")
                f_name = self._pick(cols, "name")
                f_stat = self._pick(cols, "status")
                f_sku  = self._pick(cols, "sku")
                f_price= self._pick(cols, "price")

                row = None
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # חיפוש לפי id > שם > כללי
                    if ent_id is not None and f_id:
                        cur.execute(f"SELECT * FROM {table} WHERE {f_id} = %s LIMIT 1", [ent_id])
                        row = cur.fetchone()
                    if not row and ent_name and f_name:
                        cur.execute(f"SELECT * FROM {table} WHERE {f_name} ILIKE %s LIMIT 1", [f"%{ent_name}%"])
                        row = cur.fetchone()
                    if not row:
                        # לא נכריח כללי—נחזיר "לא נמצא" במקום סתם הכל
                        return False, {"kind": "db_not_found", "msg": "לא נמצאה רשומה מתאימה ב-DB."}

                # מקרה קצר להזמנה: נצרף משלוחים
                if entity == "order":
                    lines = [f"הזמנה {row.get(f_id)} • סטטוס: {row.get(f_stat) or 'לא ידוע'}"]
                    # חפש משלוחים לפי FK
                    scol = self._cols(conn, ENTITY_TABLES["shipment"])
                    s_fk = self._pick(scol, "order_fk")
                    s_stat = self._pick(scol, "status")
                    s_track= self._pick(scol, "tracking_number")
                    s_car  = self._pick(scol, "carrier")
                    s_ts   = self._pick(scol, "shipped_ts")
                    s_id   = self._pick(scol, "id")
                    if s_fk:
                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute(
                                f"SELECT * FROM {ENTITY_TABLES['shipment']} WHERE {s_fk} = %s ORDER BY {s_id or s_fk} DESC LIMIT 5",
                                [row.get(f_id)]
                            )
                            ships = cur.fetchall() or []
                        if ships:
                            for s in ships:
                                parts = []
                                if s_stat and s.get(s_stat):  parts.append(f"סטטוס משלוח: {s[s_stat]}")
                                if s_track and s.get(s_track):parts.append(f"מס׳ מעקב: {s[s_track]}")
                                if s_car and s.get(s_car):    parts.append(f"מוביל: {s[s_car]}")
                                if s_ts and s.get(s_ts):      parts.append(f"נשלח: {s[s_ts]}")
                                if parts: lines.append(" | ".join(parts))
                        else:
                            lines.append("אין משלוחים להזמנה זו.")
                    return True, {"text": "\n".join(lines)}

                # מקרה קצר למוצר: נצרף מלאי אם יש
                if entity == "product":
                    lines = []
                    base = f"מוצר: {row.get(f_name) or row.get(f_id)}"
                    if f_sku and row.get(f_sku): base += f" (SKU: {row[f_sku]})"
                    lines.append(base)
                    if f_price and row.get(f_price) is not None:
                        lines.append(f"מחיר: {row[f_price]}")
                    # מלאי
                    icol = self._cols(conn, ENTITY_TABLES["inventory"])
                    q_col = self._pick(icol, "quantity")
                    p_fk  = self._pick(icol, "product_fk")
                    if q_col and p_fk and f_id:
                        with conn.cursor(cursor_factory=RealDictCursor) as cur:
                            cur.execute(
                                f"SELECT {q_col} FROM {ENTITY_TABLES['inventory']} WHERE {p_fk} = %s ORDER BY 1 DESC LIMIT 1",
                                [row.get(f_id)]
                            )
                            inv = cur.fetchone()
                        if inv:
                            lines.append(f"מלאי זמין: {inv.get(q_col)}")
                        else:
                            lines.append("אין רשומת מלאי מתאימה.")
                    return True, {"text": " • ".join(lines)}

                # ברירת מחדל תמציתית לכל היתר
                pieces = [f"{entity}: {row.get(f_name) or row.get(f_id)}"]
                if f_stat and row.get(f_stat): pieces.append(f"סטטוס: {row[f_stat]}")
                return True, {"text": " • ".join(pieces)}

        except Exception as e:
            return False, {"kind": "db_error", "msg": f"שגיאת DB: {e}"}

    # -------- RAG (תמציתי) --------
    def _retrieve_with_hits(self, query: str, top_k: int, ctx_chars: int) -> Tuple[List[str], List[Dict[str, Any]]]:
        if not self.index or not self.meta or top_k <= 0:
            return [], []
        vec = self._embed_one(query)
        q = np.array([vec], dtype="float32")
        D, I = self.index.search(q, top_k)
        ctx, hits = [], []
        for score, idx in zip(D[0], I[0]):
            if idx == -1: continue
            item = self.meta[idx]
            text = (item.get("text") or item.get("chunk") or "").strip()
            if ctx_chars > 0: text = text[:ctx_chars]
            ctx.append(text)
            hits.append({"score": float(score), "kind": item.get("kind"), "id": item.get("id")})
        return ctx, hits

    @staticmethod
    def _build_prompt(query: str, contexts: List[str]) -> str:
        block = "\n\n".join([f"[קונטקסט {i+1}]\n{c}" for i,c in enumerate(contexts)]) if contexts else "אין קונטקסט."
        return f"ענ/י בקצרה ובעברית פשוטה על בסיס המידע שלמטה.\n\nשאלה: {query}\n\n{block}\n\nתשובה:"

    def _generate(self, prompt: str) -> str:
        r = requests.post(f"{OLLAMA_BASE}/api/generate", json={
            "model": GEN_MODEL, "prompt": prompt, "stream": False,
            "options": {"num_predict": GEN_MAX_TOKENS, "temperature": GEN_TEMPERATURE}
        }, timeout=OLLAMA_TIMEOUT)
        r.raise_for_status()
        js = r.json()
        return (js.get("response") or "").strip()

    def _embed_one(self, text: str) -> List[float]:
        r = requests.post(f"{OLLAMA_BASE}/api/embeddings", json={"model": EMBED_MODEL, "input": text},
                          timeout=OLLAMA_TIMEOUT)
        r.raise_for_status()
        js = r.json()
        if "embedding" in js: return js["embedding"]
        if "data" in js and js["data"] and "embedding" in js["data"][0]: return js["data"][0]["embedding"]
        raise RuntimeError("unexpected embeddings response")

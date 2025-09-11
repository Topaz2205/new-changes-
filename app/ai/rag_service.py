import requests
import numpy as np
from .retriever import Retriever

EMBED_MODEL = "nomic-embed"
GEN_MODEL   = "llama3.1"

def embed_query(q: str):
    r = requests.post("http://localhost:11434/api/embeddings",
                      json={"model": EMBED_MODEL, "input": q}, timeout=60)
    r.raise_for_status()
    data = r.json()
    vec = data.get("embedding") or data["embeddings"][0]
    return np.array(vec, dtype="float32")

def generate_answer(question: str, contexts: list[dict]):
    context_text = "\n".join(f"- {c['text']}" for c in contexts)
    prompt = f"""אתה עוזר תפעולי למערכת ordersync.
ענה רק לפי הקטעים הבאים. אם אין תשובה—אמור שלא נמצא.
שאלה: {question}
קטעים רלוונטיים:
{context_text}
ענה בעברית, קצר ולעניין, והוסף בסוף 'מקורות:' עם (kind,id) עבור כל קטע ששימש."""
    r = requests.post("http://localhost:11434/api/generate",
                      json={"model": GEN_MODEL, "prompt": prompt, "stream": False}, timeout=120)
    r.raise_for_status()
    return r.json()["response"]

class RAGService:
    def __init__(self):
        self.ret = Retriever()

    def ask(self, question: str, top_k=6):
        qv = embed_query(question)
        hits = self.ret.search(qv, top_k=top_k)
        answer = generate_answer(question, hits)
        return {"answer": answer, "sources": hits}

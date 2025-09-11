import os, json
import numpy as np
import faiss

BASE_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE_DIR, "index.faiss")
META_PATH  = os.path.join(BASE_DIR, "meta.json")

class Retriever:
    def __init__(self):
        if not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)):
            raise RuntimeError("Index/metadata not found. Run index_data.py first.")
        self.index = faiss.read_index(INDEX_PATH)
        with open(META_PATH, "r", encoding="utf-8") as f:
            self.meta = json.load(f)

    def search(self, query_vec: np.ndarray, top_k=6):
        # query_vec shape: (D,)
        v = query_vec.astype("float32").reshape(1, -1)
        faiss.normalize_L2(v)
        D, I = self.index.search(v, top_k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1: 
                continue
            rec = self.meta[idx]
            hits.append({"score": float(score), "text": rec["text"], "kind": rec["kind"], "id": rec["id"]})
        return hits

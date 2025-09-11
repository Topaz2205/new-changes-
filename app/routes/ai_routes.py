# app/routes/ai_routes.py

from flask import Blueprint, request, jsonify, render_template
import requests

# הגדרה לפני שימוש בדקורטורים
ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

_rag_service = None
def _get_rag():
    global _rag_service
    if _rag_service is None:
        from app.ai.rag_service import RAGService
        _rag_service = RAGService()
    return _rag_service

@ai_bp.route("/", methods=["GET"])
def assistant_page():
    return render_template("ai_assistant.html")

@ai_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    q = (data.get("query") or "").strip()
    if not q:
        return jsonify({"error": "missing query"}), 400
    try:
        rag = _get_rag()
        out = rag.ask(q)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@ai_bp.route("/health", methods=["GET"])
def ai_health():
    try:
        r = requests.get("http://localhost:11434/api/version", timeout=1.5)
        v = r.json().get("version", "?")
        return jsonify({"ok": True, "version": v})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 503
